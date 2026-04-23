import App from './App'
import './static/iconfont/iconfont.css'
// #ifndef VUE3
import Vue from 'vue'
Vue.config.productionTip = false
Vue.filter('formatCount', function(value) {
	if (value >= 10000 && value <= 100000000) {
		value /= 10000;
		return value.toFixed(1) + '万';
	} else if (value >= 100000000) {
		value /= 100000000;
		return value.toFixed(1) + '亿';
	}
})


//登录页面注册
import login from './components/login/login.vue'
Vue.component("login",login)
//引入store
import store from './store/index.js'
//import audio from './store/audioContext.js'
//拦截器
// import interceptor from './common/interceptor.js'
// Vue.use(interceptor,app)



App.mpType = 'app'
const app = new Vue({
	...App,
	store
})
app.$mount()
// #endif

// #ifdef VUE3
import {
	createSSRApp
} from 'vue'
export function createApp() {
	const app = createSSRApp(App)
	return {
		app
	}
}
// #endif

