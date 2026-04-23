import Vue from 'vue'
import Vuex from 'vuex'
import {increaseTrackcounts} from '../common/api.js'
// import { setCurrentTime } from '../common/audioContext'

Vue.use(Vuex)

const store = new Vuex.Store({
	state: {
		// 用户信息
		userinfo:uni.getStorageSync('userinfo')||
		{
			id:'',
			openid:'',
			sessionkey:'',
			nickName:'',
			mobile:'',
			createtime:'',
			userpic:''
		},
		checkSession:uni.getStorageSync('checkSession') || false,
		
		//歌曲
		innerAudioContext:uni.createInnerAudioContext(), //创建播放器对象
		isPlaying:uni.getStorageSync('isPlaying')|| false,
		isPlayEnd:uni.getStorageSync('isPlayEnd')|| false,
		isChanging:uni.getStorageSync('isChanging')|| false,
		currentTime:uni.getStorageSync('currentTime')|| 0,
		currentTimeStr: uni.getStorageSync('currentTimeStr')||'00:00',
		duration: uni.getStorageSync('duration')||0,
		timeStr:uni.getStorageSync('timeStr')|| '00:00',
		thisSong: uni.getStorageSync('thisSong')||{},
		ids:uni.getStorageSync('ids')|| [],
		songlist:uni.getStorageSync('songlist')|| [],
		mode:"iconfont icon-loop"
	},
	getters: {

	},
	mutations: {
		// 将用户信息持久化存储到本地
		saveUserInfoToStorge(state) {
			var str=state.userinfo;
			if(typeof str==='string'){
				uni.setStorageSync('userinfo', state.userinfo)
			}else{
			 uni.setStorageSync('userinfo', JSON.stringify(state.userinfo))
			 }
			//console.log("持久化userinfo"+JSON.stringify(state.userinfo))
			//uni.setStorageSync('userinfo', state.userinfo)
		},
		saveCheckSessionToStorge(state) {
			uni.setStorageSync('checkSession', state.checkSession)
		},
		//歌曲信息持久化
		saveInnerAudioContextToStorge(state){
			uni.setStorageSync('innerAudioContext',state.innerAudioContext);
		},
		saveIsPlayingToStorge(state){
			uni.setStorageSync('isPlaying',state.isPlaying);
		},
		saveIsPlayEndToStorge(state){
			uni.setStorageSync('isPlayEnd',state.isPlayEnd);
		},
		saveIsChangingToStorge(state){
			uni.setStorageSync('isChanging',state.isChanging);
		},
		saveCurrentTimeToStorge(state){
			uni.setStorageSync('currentTime',state.currentTime);
		},
		saveCurrentTimeStrToStorge(state){
			uni.setStorageSync('currentTimeStr',state.currentTimeStr);
		},
		saveDurationToStorge(state){
			uni.setStorageSync('duration',state.duration);
		},
		saveTimeStrToStorge(state){
			uni.setStorageSync('timeStr',state.timeStr);
		},
		saveThisSongToStorge(state){
			var str=state.thisSong;
			if(typeof str==='string'){
				uni.setStorageSync('thisSong', state.thisSong)
			}else{
			 uni.setStorageSync('thisSong', JSON.stringify(state.thisSong))
			 }
		},
		saveIdsToStorge(state){
			uni.setStorageSync('ids',state.ids);
		},
		saveSonglistToStorge(state){
			var str=state.songlist;
			if(typeof str==='string'){
				uni.setStorageSync('songlist', state.songlist)
			}else{
			 uni.setStorageSync('songlist', JSON.stringify(state.songlist))
			 }
			
			//uni.setStorageSync('songlist',state.songlist);
		},
		saveThisSongToStorge(state){
			uni.setStorageSync('thisSong',state.thisSong)
		},
		saveModeToStorge(state){
			uni.setStorageSync('mode',state.mode);
		},
		
		
		// 更新用户信息
		updateUserInfo(state, userinfo) {
			state.userinfo = userinfo
			this.commit('saveUserInfoToStorge')
		},		
		updateCheckSession(state, checkSession) {
			state.checkSession = checkSession
			this.commit('saveCheckSessionToStorge')
		},
		
		//设置播放列表
		setIds(state, ids) {
			state.ids = ids;
			this.commit('saveIdsToStorge');
		},
		setSonglist(state,songlist){
			state.songlist=songlist;
			this.commit('saveSonglistToStorge');
		},
		setThisSong(state,song){
			state.thisSong=song;
			this.commit('saveThisSongToStorge');
		},
		//设置播放路径
		setMusicUrl(state, song) {
			let preSrc=state.innerAudioContext.src;
			//播放器引入url
			state.thisSong = song;
			state.innerAudioContext.src = song.url;
			//初始化播放进度
			console.log("preScr=="+preSrc);
			console.log("thisSrc=="+state.thisSong.url)
			//设置开始播放时间，如果切换音乐则从头播放，否则继续播放
			if(preSrc==song.url){
				state.innerAudioContext.startTime = state.currentTime;
			}else{
				state.innerAudioContext.seek(0)
				state.innerAudioContext.startTime=0;
				
			}	
			//获取当前音乐总时长
			state.duration=state.innerAudioContext.duration;			
			state.innerAudioContext.onPlay(() => {
				//state.isPlaying=true;
				console.log('开始播放');		
			});
			//音频进入可以播放状态
			state.innerAudioContext.onCanplay(() => {
				let timeid = setInterval(() => {
					if (state.innerAudioContext.duration) {
						clearInterval(timeid)
						//将获取的歌曲时长格式化
						state.duration = state.innerAudioContext.duration || 0;
						let num = state.duration.toFixed(0);
						let second = num % 60;
						if (second < 10) second = '0' + second;
						let min = Math.floor(num / 60);
						if (min < 10) min = '0' + min;
						state.timeStr= min + ":" + second;
					}
				}, 800)
			});
			//开始播放
			state.innerAudioContext.play(); 
			//设置播放状态
			state.isPlaying = true;
			state.innerAudioContext.onEnded(() => {
				state.currentTime = 0;
				state.isPlaying = false;
				state.isPlayEnd = true;
				//一首歌自然播放结束，增加播放量
				increaseTrackcounts(state.thisSong.id).then(res=>{
					console.log(state.thisSong.name+"的播放量增一")
				})
			});
			state.innerAudioContext.onError(res => {
				state.isPlaying = false;
				console.log("播放错误")
			});
			//将歌曲信息持久化
			 this.commit('saveThisSongToStorge');
		},
		//修改播放进度
		// setSchedule(state, num) {
		// 	state.schedule = state.max * num;
		// 	state.music.currentTime = state.schedule;
		// },
		//更新播放时长
		setDuration(state,num){
			state.duration=num;
			this.commit('saveDurationToStorge');
		},
		//更新当前播放时间
		setCurrentTime(state,num){
			state.currentTime=num;
			this.commit('saveCurrentTimeToStorge');
		},
		setTimeStr(State,timeStr){
			state.timeStr=timeStr;
			this.commit('saveTimeStrToStorge');
		},
		//修改播放状态
		setPause(state){
			state.innerAudioContext.pause();
			state.isPlaying = false;
			this.commit('saveIsPlayingToStorge');
			this.commit('saveInnerAudioContextToStorge');
		},
		setPlay(state){
			state.isPlaying = true;
			state.innerAudioContext.play();
			state.isPlayEnd=false;
			this.commit('saveIsPlayingToStorge');
			this.commit('saveInnerAudioContextToStorge');
			this.commit('saveIsPlayEndToStorge');
		},
		setIsPlaying(state,isPlaying){
			state.isPlaying=isPlaying;
			this.commit('saveIsPlayingToStorge');
		},
		
		
		//停止
		setStop(state) {
			state.innerAudioContext.stop();
			state.isPlaying = false;
			this.commit('saveIsPlayingToStorge');
			this.commit('saveInnerAudioContextToStorge');
		},
		//拖动进度条
		setOnchanging(state) {
			state.isChanging = true;
			this.commit('saveIsChangingToStorge');
		},
		setIsChanging(state,isChanging){
			state.isChanging=isChanging;
			this.commit('saveIsChangingToStorge');
		},
		setMode(state, mode) {
			state.mode = mode;
			this.commit('saveModeToStorge');
		},
		onchange(state,e) {
			// console.log(e.detail.value);
			// console.log(typeof e.detail.value);
			state.innerAudioContext.seek(e.detail.value);
			state.isChanging= false;
			state.innerAudioContext.currentTime=e.detail.value;
			state.currentTime=e.detail.value
			this.commit('saveIsChangingToStorge');
			this.commit('saveCurrentTimeToStorge')
			this.commit('saveInnerAudioContextToStorge');
		},

	},
	actions: {
		// userLoginAction(context, userInfo) {
		// 	context.commit('userLogin', userInfo)
		// },
		// userLogoutAction(context) {
		// 	context.commit('userLogout')
		// }
		//暂停当前播放的音频
		pause(state) {
			this.commit("setPause")
		},
		//开始播放音频
		play(state) {
			if(state.isPlaying){
				this.commit('setPause');
				return;
			}
			this.commit("setPlay")
			
		},
		//停止
		stop(state){
			this.commit("setStop");
		},
		//改进度
		onchanging(state) {
			this.commit("setOnchanging")
		},
		doChange(state,e){
			this.commit("onchange",e)
		}
	}
})

export default store
