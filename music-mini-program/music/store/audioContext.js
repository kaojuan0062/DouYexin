import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)
const audio = new Vuex.Store({
	namespaced:true,
	state: {

		innerAudioContext: uni.createInnerAudioContext(), //创建播放器对象
		isPlaying: false,
		isPlayEnd: false,
		isChanging: false,
		currentTime: 0,
		currentTimeStr: '00:00',
		duration: 100,
		timeStr: '00:00:00',
		thisSong: {},
		ids: [],
		songList: []

	},
	mutations: {
		//设置播放列表
		setList(state, ids) {
			state.ids = ids;
		},
		//设置播放路径
		setMusicUrl(state, song) {
			console.log("storeAudioContext==" + JSON.stringify(song))
			//设置索引
			//state.index=index;
			//设置路径
			//state.url = state.list[index].url;
			//播放器引入url
			state.song = song;
			state.innerAudioContext.src = state.song.url;
			//初始化播放进度
			state.innerAudioContext.startTime = 0;
			state.innerAudioContext.onPlay(() => {
				console.log('开始播放');

			});
			state.innerAudioContext.onCanplay(() => {
				let timeid = setInterval(() => {
					if (state.innerAudioContext.duration) {
						clearInterval(timeid)
						state.duration = innerAudioContext.duration || 0;
						console.log(duration)
						//timeStr = this.formatSecond(this.duration);
					}
				}, 500)
			});
			//开始播放
			state.innerAudioContext.play(); //执行播放
			//设置播放状态
			state.isPlaying = true;
			//获取播放进度
			state.innerAudioContext.onTimeUpdate(() => {
				//设置总时长
				//state.duration = state.music.duration;
				//修改进度
				state.currentTime = state.innerAudioContext.currentTime;
			})
			state.innerAudioContext.onEnded(() => {
				state.currentTime = 0;
				state.currentTimeStr = this.formatTime(this.currentTime);
				state.isPlaying = false;
				state.isPlayEnd = true;
			});
			this.innerAudioContext.onError(res => {
				state.isPlaying = false;
				console.log("播放错误")
				// console.log(res.errMsg);
				// console.log(res.errCode);
			});
			//return state.innerAudioContext;
		},
		//修改播放进度
		// setSchedule(state, num) {
		// 	state.schedule = state.max * num;
		// 	state.music.currentTime = state.schedule;
		// },
		//开始播放音频
		play(state) {
			if(state.isPlaying){
				this.commit('pause');
				return;
			}
			state.isPlaying = true;
			state.innerAudioContext.play();
			state.isPlayEnd=false
		},
		//暂停当前播放的音频
		pause(state) {
			state.innerAudioContext.pause();
			state.isPlaying=false;
		},
		//停止
		stop(state) {
			state.innerAudioContext.stop();
			state.isPlaying = false;
		},
		//拖动进度条
		onchanging(state) {
			state.isChanging = true;
		},
		whenchange(state,e) {
			console.log(e.detail.value);
			console.log(typeof e.detail.value);
			state.innerAudioContext.seek(e.detail.value);
			state.isChanging= false;
			
			state.currentTime=e.detail.value
		},
		
		
		formatTime(num) {
			//格式化时间格式
			num = num.toFixed(0);
			let second = num % 60;
			if (second < 10) second = '0' + second;
			let min = Math.floor(num / 60);
			if (min < 10) min = '0' + min;
			return min + ":" + second;
		},
	}
})
export default audio
