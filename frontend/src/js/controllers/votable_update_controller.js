import Creator from './votable_creation_controller';

const POST_URL = '/api-auth/submit/post/';
const TOPIC_URL = '/api-auth/submit/topic/';

export default class extends Creator{
    connect(){
        super.connect();
    }
}