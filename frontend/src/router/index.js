import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/team/persons',
    name: 'Persons',
    component: () => import('../views/team/Persons.vue')
  },
  {
    path: '/team/groups',
    name: 'Groups',
    component: () => import('../views/team/Groups.vue')
  },
  {
    path: '/team/ability',
    name: 'Ability',
    component: () => import('../views/team/Ability.vue')
  },
  {
    path: '/project/versions',
    name: 'Versions',
    component: () => import('../views/project/Versions.vue')
  },
  {
    path: '/project/iterations',
    name: 'Iterations',
    component: () => import('../views/project/Iterations.vue')
  },
  {
    path: '/project/tasks',
    name: 'Tasks',
    component: () => import('../views/project/Tasks.vue')
  },
  {
    path: '/architecture/modules',
    name: 'Modules',
    component: () => import('../views/architecture/Modules.vue')
  },
  {
    path: '/architecture/features',
    name: 'Features',
    component: () => import('../views/architecture/Features.vue')
  },
  {
    path: '/architecture/fields',
    name: 'Fields',
    component: () => import('../views/architecture/Fields.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
