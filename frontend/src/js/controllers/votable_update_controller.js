import Creator from './votable_creation_controller';

const POST_URL = '/api/post/edit/';
const TOPIC_URL = '/api/topic/edit/';

export default class extends Creator{
    connect(){
        super.connect();
    }
    setUpURL() {
        this.url = this.isPost? POST_URL: TOPIC_URL;
    }
}