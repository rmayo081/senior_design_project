import axios from 'axios'

const api = axios.create({ baseURL: 'https://localhost/api/v1' })

export default api