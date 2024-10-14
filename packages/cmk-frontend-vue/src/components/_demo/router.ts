/**
 * Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */

import { createRouter, createWebHistory } from 'vue-router'

import DemoEmpty from './DemoEmpty.vue'
import DemoAlertBox from './DemoAlertBox.vue'
import DemoIconButton from './DemoIconButton.vue'
import DemoSlideIn from './DemoSlideIn.vue'
import DemoFormEditAsync from './DemoFormEditAsync.vue'
import DemoToggleButtonGroup from './DemoToggleButtonGroup.vue'
import DemoCmkButton from './DemoCmkButton.vue'
import DemoCmkIcon from './DemoCmkIcon.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DemoEmpty
    },
    {
      path: '/alertbox',
      name: 'AlertBox',
      component: DemoAlertBox
    },
    {
      path: '/iconbutton',
      name: 'IconButton',
      component: DemoIconButton
    },
    {
      path: '/slidein',
      name: 'SlideIn',
      component: DemoSlideIn
    },
    {
      path: '/formeditasync',
      name: 'FormEditAsync',
      component: DemoFormEditAsync
    },
    {
      path: '/cmkicon',
      name: 'CmkIcon',
      component: DemoCmkIcon
    },
    {
      path: '/togglebuttongroup',
      name: 'ToggleButtonGroup',
      component: DemoToggleButtonGroup
    },
    {
      path: '/button',
      name: 'CmkButton',
      component: DemoCmkButton
    }
  ]
})

export default router
