import lazyLoading from './lazyLoading'

export default {
  name: 'InfraryComposer',
  path: '/infrary-compose',
  component: lazyLoading('environment/InfraryComposer'),
  meta: {
    default: false,
    title: 'Compose',
    iconClass: 'vuestic-icon vuestic-icon-files'
  }
}
