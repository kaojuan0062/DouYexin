const install = (Vue, vm) => {
	// 此为自定义配置参数，具体参数见上方说明
	// Vue.prototype.$u.http.setConfig({
	// 	// ......
	// });
	
	// 请求拦截部分，如配置，每次请求前都会执行
	Vue.prototype.$u.http.interceptor.request = (config) => {
		// 引用token
		// 方式四，如果token放在了Storage本地存储中，拦截是每次请求都执行的
		// 所以哪怕您重新登录修改了Storage，下一次的请求将会是最新值
		const token = uni.getStorageSync('token');
		config.header.Authorization="Beaer"+token;
		config.header.Accept="appliction/json";
		// config.header.token = token;
		//config.header.Token = 'xxxxxx';
		
		// 可以对某个url进行特别处理，此url参数为this.$u.get(url)中的url值
		//if(config.url == '/user/login') config.header.noToken = true;
		// 最后需要将config进行return
		return config;
		// 如果return一个false值，则会取消本次请求
		// if(config.url == '/user/rest') return false; // 取消某次请求
	}
}

export default {
	install
}