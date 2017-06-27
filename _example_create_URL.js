import qs from 'qs' // 

require('dotenv').config()


// https://accounts.google.com/o/oauth2/v2/auth?client_id=1015923915619-1ub1gu9o670gvnsiaqi1dtlmteugve2j.apps.googleusercontent.com&response_type=code&access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile%20https%3A%2F%2Fmail.google.com%2F%20https%3A%2F%2Fwww.google.com%2Fm8%2Ffeeds%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fconnected&prompt=consent

const GOOGLE_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://mail.google.com/',
    'https://www.google.com/m8/feeds',
    'https://www.googleapis.com/auth/calendar',
]


function main() {
    const GOOGLE_OAUTH_BASE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'

    if (!process.env.GOOGLE_ID) throw new Error('No GOOGLE_ID environment variable')

    const queryParams = {
        client_id: process.env.GOOGLE_ID,
        response_type: 'code',
        access_type: 'offline',
        scope: GOOGLE_OAUTH_SCOPES.join(' '),
        redirect_uri: 'http://localhost:5000/connected',
        prompt: 'consent',
    }

    const encodedQueryParams = qs.stringify(queryParams)

    console.log(`${GOOGLE_OAUTH_BASE_URL}?${encodedQueryParams}`)
}


if (require.main === module) {
    main()
}