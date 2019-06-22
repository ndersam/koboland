from django.contrib.staticfiles.testing import (
    StaticLiveServerTestCase
)
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from main import factories
from main.api import VotableVoteAPI
from koboland.test_helpers import create_session_cookie

DRIVER_PATH = 'C:\\Program Files\\Mozilla Firefox WebDriver\\geckodriver.exe'


class LoggedInLiveServerTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver(executable_path=DRIVER_PATH)

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        self.login(self.user)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login(self, user):
        # self.client.force_login(user=user)
        session_cookie = create_session_cookie(username=user.username, password='top_secret')
        self.driver.get(f'{self.live_server_url}/non-existent-url/')
        self.driver.add_cookie(session_cookie)
        self.driver.refresh()
        self.driver.get(f'{self.live_server_url}/')
        # cookie = self.client.cookies['sessionid']
        # self.driver.get(
        #     f'{self.live_server_url}/admin/')  # selenium will set cookie domain based on current page domain
        # self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        # self.driver.refresh()  # need to update page for logged in user
        # self.driver.get(self.live_server_url + '/admin/')

    def wait_for(self, css_selector):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )


class TestVotableActionController(LoggedInLiveServerTestCase):

    def test_like_topic_works_correctly(self):
        board = factories.BoardFactory()
        topic = factories.TopicFactory(author=self.user, board=board)

        self.driver.get(f'{self.live_server_url}{topic.get_absolute_url()}')

        info_elem = self.wait_for('[data-item-class="topic"]')
        btn_like = self.driver.find_element_by_css_selector('[data-item-class="topic"] > button:first-of-type')
        like_count = self.driver.find_element_by_css_selector(
            '[data-item-class="topic"] > button:first-of-type + span')
        self.assertIsNotNone(btn_like)
        self.assertIsNotNone(like_count)
        self.assertEquals(like_count.get_attribute('innerHTML'), '')
        self.assertEquals(info_elem.get_attribute('data-item-like-count'), '0')
        self.assertEquals(info_elem.get_attribute('data-item-vote-state'), '')

        btn_like.click()
        self.assertEquals(like_count.get_attribute('innerHTML'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-like-count'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-vote-state'), str(VotableVoteAPI.LIKE))

        topic.refresh_from_db()
        self.assertEquals(topic.likes, 1)

    def test_dislike_topic_works_correctly(self):
        board = factories.BoardFactory()
        topic = factories.TopicFactory(author=self.user, board=board)

        self.driver.get(f'{self.live_server_url}{topic.get_absolute_url()}')

        info_elem = self.driver.find_element_by_css_selector('[data-item-class="topic"]')
        btn_dislike = self.driver.find_element_by_css_selector('[data-item-class="topic"] > button:nth-of-type(2)')
        dislike_count = self.driver.find_element_by_css_selector(
            '[data-item-class="topic"] > button:nth-of-type(2) + span')
        self.assertIsNotNone(btn_dislike)
        self.assertIsNotNone(dislike_count)
        self.assertEquals(dislike_count.get_attribute('innerHTML'), '')
        self.assertEquals(info_elem.get_attribute('data-item-dislike-count'), '0')
        self.assertEquals(info_elem.get_attribute('data-item-vote-state'), '')

        btn_dislike.click()
        self.assertEquals(dislike_count.get_attribute('innerHTML'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-dislike-count'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-vote-state'), str(VotableVoteAPI.DISLIKE))

        self.driver.implicitly_wait(10)
        topic.refresh_from_db()
        self.assertEquals(topic.dislikes, 1)

    def test_share_topic_works_correctly(self):
        board = factories.BoardFactory()
        topic = factories.TopicFactory(author=self.user, board=board)

        self.driver.get(f'{self.live_server_url}{topic.get_absolute_url()}')

        info_elem = self.driver.find_element_by_css_selector('[data-item-class="topic"]')
        btn_share = self.driver.find_element_by_css_selector('[data-item-class="topic"] > button:nth-of-type(3)')
        share_count = self.driver.find_element_by_css_selector(
            '[data-item-class="topic"] > button:nth-of-type(3) + span')
        self.assertIsNotNone(btn_share)
        self.assertIsNotNone(share_count)
        self.assertEquals(share_count.get_attribute('innerHTML'), '')
        self.assertEquals(info_elem.get_attribute('data-item-share-count'), '0')
        self.assertEquals(info_elem.get_attribute('data-item-shared'), '0')

        btn_share.click()
        self.assertEquals(share_count.get_attribute('innerHTML'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-share-count'), '1')
        self.assertEquals(info_elem.get_attribute('data-item-shared'), '1')

        topic.refresh_from_db()
        self.assertEquals(topic.shares, 1)
