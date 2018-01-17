import lazyLoading from './lazyLoading'

export default {
  name: 'Servers',
  meta: {
    expanded: false,
    hide: true,
    title: 'Servers',
    iconClass: 'vuestic-icon vuestic-icon-forms'
  },
  children: [
    {
      name: 'Create',
      path: '/servers/create',
      component: lazyLoading('servers/create/Create'),
      meta: {
        title: 'Create'
      }
    }
  ]
}

