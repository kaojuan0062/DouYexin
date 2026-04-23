<template>
	<view class="play">
		<view class="fixbg" :style="{backgroundImage:'url('+thisSong.picurl+')'}"></view>
		<musichead title="歌单" :icon="icon" color="white"></musichead>
		<view class="container">
			<view class="play-cover">
				<view class="music-top">
					<view class="music-name">
						{{thisSong.name}}
					</view>
					<view class="music-artist">
						{{thisSong.artistName}}
					</view>
				</view>
				<swiper class="play-box">
					<swiper-item class="imgbox">
						<view class="music-play">
							<image :src="thisSong.picurl" :class="{'music-play-pause':!isPlaying}"></image>
							<!-- <text class="iconfont icon-zanting"></text> -->
							<view class="">

							</view>

						</view>
					</swiper-item>
					<!-- :class="index==lrcIndex?'lrcshow':''" -->
					<swiper-item class="lrcbox">
						<scroll-view scroll-y="false" :scroll-top="top" touch-action='none' cancelable='false'>
							<view v-for="(item,index) in lrcData" :key="index">
								<view :class="index==lrcIndex?'lrcShow':''">{{item[1]}}</view>
							</view>
						</scroll-view>
					</swiper-item>
				</swiper>
				<!-- 进度条 -->
				<view class="timebox">
					<view class="start_time">{{currentTimeStr}}</view>
					<slider block-size="12" activeColor="#c4d39b" :min="0" :max="duration" @changing="onchanging"
						@change="onchange" :value="position">

					</slider>
					<view class="end_time">{{timeStr}}</view>
				</view>
				<!-- 播放按钮 -->
				<view class="btnbox">
					<text @tap="playMode" :class="mode" class="small"></text>
					<text @tap="preSong(thisSong.id)" class="iconfont icon-shangyishou"></text>
					<text @tap="play" :class="playImage"></text>
					<text @tap="nextSong(thisSong.id)" class="iconfont icon-xiayishou"></text>
					<text @tap="showPopup" class="iconfont icon-playlist small"></text>
				</view>
			</view>
		</view>
		<!-- 底部弹窗播放列表 -->
		<uni-popup ref="popup" type="bottom">
			<!-- <view class="popup-content" :class="{ 'popup-height': type === 'left' || type === 'right' }">
				<text>popup 内容</text>
			</view> -->
			<view class="popup-content">
				<view class="popup-top">
					<text>当前播放</text>
				</view>
				<scroll-view scroll-y="true">
					<view class="popup-item" v-for="(item,index) in songlist" :key="index">

						<view class="popup-item-song" @tap="playThis(item.id)">
							<text>{{item.name}}</text>

							<text>-{{item.artistName}}</text>
						</view>
						<text @tap="deleteThis(item.id)" class="iconfont icon-cancel"></text>
					</view>
				</scroll-view>
			</view>
		</uni-popup>

	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import {
		getThisSong,
		getSongs
	} from '../../common/api.js'
	const audioUrl = 'http://music.163.com/song/media/outer/url?id=65234'
	let thisthis = null;
	// var _audioContext = null;
	//var innerAudioContext =uni.createAudioContext();;
	export default {

		data() {
			return {
				icon: true,
				thisSong: {},
				lrcData: [],
				lrcIndex: -1,
				top: '',
				thisId: '',
				ids: [],
				mode: "iconfont icon-loop",
				songlist: [],
				// thisIndex:'',
				// nextIndex:'',
				// preIndex:'',

				title: "innerAudioContext",
				isPlaying: false,
				isPlayEnd: false,
				currentTime: 0,
				currentTimeStr: '00:00',
				duration: 100,
				timeStr: '00:00:00',


			}
		},
		computed: {

			position() {
				return this.isPlayEnd ? 0 : this.currentTime;
			},
			playImage() {
				return this.isPlaying ? "iconfont icon-play" : "iconfont icon-zanting"
			},
		},
		// onShow(){
		// 	var idList=this.ids;
		// 	console.log("onShow"+idList);
		// 	//当前位置
		// 	var index=-1;
		// 	for(var i=0;i<idList.length;i++){
		// 		if(this.thisIndex==idList[i]){
		// 			index=i;
		// 			break;
		// 		}
		// 	}
		// 	this.thisId=(index==idList.length-1)?idList[0]:idList[index-1];
		// },
		onLoad(options) {
			thisthis = this;
			console.log("onLoad");
			//console.log(options.songId+"=="+options.ids);
			this.thisId = options.songId;
			//播放器设置
			this._isChanging = false;
			this._audioContext = null;
			//获取歌曲
			getThisSong(options.songId).then(res => {
				if (res != null) {
					this.thisSong = res;
					this.lrcshow();
					this.createAudio();
				}

				//console.log("播放页面获取值", this.thisSong)
			})
			//获取当前歌曲列表
			this.ids = options.ids.split(',');
			// getSongs(options.pId).then(res => {
			// 	if (res != null) {
			// 		this.songlist = res;
			// 	}
			// })

			for (var i = 0; i < this.ids.length; i++) {
				getThisSong(this.ids[i]).then(res => {
					// thisthis.songlist[i]=res;
					// this.$set(thisthis.songlist,i,res);
					this.songlist.push(res);
					// console.log(this.songlist[i])
				})
			}
			console.log(this.songlist[5])


			// this.createAudio();
		},
		onUnload() {
			if (this._audioContext != null && this.isPlaying) {
				this.stop();
			}
		},
		methods: {
			// 音乐播放器
			createAudio() {
				//innerAudioContext=uni.createAudioContext();
				var innerAudioContext = this._audioContext = uni.createInnerAudioContext();
				//this._audioContext=innerAudioContext;
				this.isPlaying = true;
				innerAudioContext.autoplay = true;
				//console.log("播放器函数", this.thisSong)
				innerAudioContext.src = this.thisSong.url;
				innerAudioContext.onPlay(() => {
					console.log('开始播放'+innerAudioContext);
					
				});
				innerAudioContext.onCanplay(() => {
					let timeid = setInterval(() => {
						if (innerAudioContext.duration) {
							clearInterval(timeid)
							this.duration = innerAudioContext.duration || 0;
							console.log(this.duration)
							this.timeStr = this.formatSecond(this.duration);
						}
					}, 500)
				});
				innerAudioContext.onTimeUpdate((e) => {
					if (this._isChanging === true) {
						return;
					}
					//console.log("正在播放===",this.currentTime)
					//歌词滚动
					// var lrctime
					for (var i = 0; i < this.lrcData.length; i++) {
						//console.log(this.lrcData[i][0])
						//var thisLcr = this.lrcData[i];
						if (this.lrcData[i] == null) {} else {
							if (this.lrcData[i] != null && this.lrcData[i + 1] != null && this.lrcData[i][0] < this
								.currentTime && this.lrcData[i + 1][0] > this.currentTime) {
								//console.log(thisLcr[1])
								if (i > 0 && this.lrcData[i - 1][0] < this.lrcData[i][0] && this.lrcData[i][0] <
									this.lrcData[i + 1][0]) {
									this.lrcIndex = i;
								}
							}
							//歌词提前结束
							else if (this.currentTime > this.lrcData[this.lrcData.length - 1][0]) {
								this.lrcIndex = this.lrcData.length - 1;

							}
						}
						//拿到当前歌词下标
						var index = this.lrcIndex;
						this.top = (index - 5) * 35;

					}
					this.currentTime = innerAudioContext.currentTime || 0;
					this.duration = innerAudioContext.duration || 0;
					this.currentTimeStr = this.formatTime(this.currentTime);
					//进度条最大值
					//this.timeStr = this.formatSecond(this.duration);					

				});
				innerAudioContext.onEnded(() => {
					this.currentTime = 0;
					this.currentTimeStr = this.formatTime(this.currentTime);
					this.isPlaying = false;
					this.isPlayEnd = true;
					this.changeMusic();
				});
				innerAudioContext.onError(res => {
					this.isPlaying = false;
					this.isRotation = "music-play-pause";
					console.log("播放错误")
					// console.log(res.errMsg);
					// console.log(res.errCode);
				});
				//console.log(innerAudioContext);
				console.log(this._audioContext)
				return innerAudioContext;
			},
			onchanging() {
				this._isChanging = true;
			},
			onchange(e) {
				console.log(e.detail.value);
				console.log(typeof e.detail.value);
				this._audioContext.seek(e.detail.value);
				this._isChanging = false;
				const currTimeStr = this.formatTime(e.detail.value)
				this.currentTimeStr = currTimeStr
			},
			play() {
				if (this.isPlaying) {
					this.pause();
					return;
				}
				this.isPlaying = true;
				this._audioContext.play();
				this.isPlayEnd = false;
			},
			pause() {
				this._audioContext.pause();
				this.isPlaying = false;
			},
			stop() {
				this._audioContext.stop();
				this.isPlaying = false;
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
			/**
			 * 格式化时间 
			 * @param {String} date 原始时间格式
			 * 格式后的时间：hh:mm:ss
			 **/
			formatSecond(seconds) {
				var h = Math.floor(seconds / 3600) < 10 ? '0' + Math.floor(seconds / 3600) : Math.floor(seconds /
					3600);
				var m = Math.floor((seconds / 60 % 60)) < 10 ? '0' + Math.floor((seconds / 60 % 60)) : Math.floor((
					seconds / 60 % 60));
				var s = Math.floor((seconds % 60)) < 10 ? '0' + Math.floor((seconds % 60)) : Math.floor((seconds %
					60));
				return h + ":" + m + ":" + s;
			},
			/**
			 * 歌词
			 */
			lrcshow: function() {
				var newLrclist = [];
				if (this.thisSong.lyric != null && this.thisSong.lyric != undefined) {
					var lrclist = this.thisSong.lyric.split('\n');
					//console.log(lrclist)
					//正则表达式拆分
					var re = /\[\d{2}:\d{2}\.\d{2,3}\]/
					for (var i = 0; i < lrclist.length; i++) {
						//console.log(i+"==="+lrclist[i]);
						var lrcArray = lrclist[i].match(re);
						//判断数据不为空
						if (lrcArray != null) {
							var lrcTime = lrcArray[0];
							//console.log(lrcTime)
							if (lrcTime != null) {
								//时间转为毫秒
								var timedata = lrcTime.slice(1, -1);
								var times = timedata.split(':');
								var m = times[0];
								var s = times[1];
								var time = parseFloat(m) * 60 + parseFloat(s);
								//获取歌词
								var lrcText = lrclist[i].replace(re, "");
								//console.log(time)
								newLrclist.push([time, lrcText]);
							}

						}
					}
					//console.log(newLrclist)
					this.lrcData = newLrclist;

				}

			},
			/**
			 * 下一首
			 */
			nextSong: function(id) {

				var thisSrc = this._audioContext._src;
				this.pause();
				this._audioContext.destroy();
				//this._isChanging = true;

				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				//var idList = this.ids;
				//console.log(idList+"=="+id);
				//当前位置
				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				//this.thisId = (index == this.ids.length - 1) ? this.ids[0] : this.ids[index - 1];
				if (index == this.ids.length - 1) {
					this.thisId = this.ids[0];
				} else {
					this.thisId = this.ids[index + 1];
				}
				console.log("这一首" + this._audioContext._src);
				getThisSong(this.thisId).then(res => {
					if (res != null && res != undefined) {
						this.thisSong = res;
						console.log("下一首id" + this.thisSong.url)
						this.lrcshow();
						//this.createAudio();
						// this.isPlayEnd= false;
						this.currentTime = 0;
						// this._audioContext.seek(0);
						// //this.currentTimeStr = '00:00';
						// //this.timeStr = '00:00:00';
						// this._audioContext._src= this.thisSong.url;
						// console.log("下一首"+this._audioContext);
						// // this._audioContext._src= this.thisSong.url;
						// this._audioContext.onPlay();
						// this._audioContext.onCanplay(() => {
						// 	let timeid = setInterval(() => {
						// 		if (this._audioContext._audio.duration) {
						// 			clearInterval(timeid)
						// 			this.duration = this._audioContext._audio.duration || 0;
						// 			console.log(this.duration)
						// 			this.timeStr = this.formatSecond(this.duration);

						// 		}
						// 	}, 800)

						// })
						// this.play();
						this._isChanging = false;
						this._audioContext = null;
						this.createAudio();


					}
					//console.log("播放页面获取值", this.thisSong)
				})

			},
			/**
			 * 上一首
			 */
			preSong: function(id) {
				this.pause();
				this._audioContext.destroy();
				//this._isChanging = true;

				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				//var idList = this.ids;
				//console.log(idList+"=="+id);
				//当前位置
				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				//this.thisId = (index == this.ids.length - 1) ? this.ids[0] : this.ids[index - 1];
				if (index == 0) {
					this.thisId = this.ids[this.ids.length - 1];
				} else {
					this.thisId = this.ids[index - 1];
				}
				console.log("这一首" + this._audioContext._src);
				getThisSong(this.thisId).then(res => {
					if (res != null) {
						this.thisSong = res;
						this.lrcshow();
						this.currentTime = 0;
						this._isChanging = false;
						this._audioContext = null;
						this.createAudio();
					}
					//console.log("播放页面获取值", this.thisSong)
				})
			},
			/**
			 * 歌曲播完后切换
			 */
			changeMusic: function() {
				this.pause();

				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				switch (this.mode) {
					case "iconfont icon-loop":
						this.nextSong(this.thisSong.id);
						break;
					case "iconfont icon-single":
						//播放器重置
						this._isChanging = true;
						this.currentTime = 0;
						this._audioContext.seek(0);
						this.play();
						this._isChanging = false;
						break;
					case "iconfont icon-random":
						var index = Math.floor(Math.random() * (this.ids.length - 1));
						//console.log("随机播放"+this.thisId)
						this._audioContext.destroy();
						getThisSong(this.ids[index]).then(res => {
							this.thisSong = res;
							this.lrcshow();
							//播放器重置
							this.currentTime = 0;
							this._isChanging = false;
							this._audioContext = null;
							this.createAudio();
						})

						break;
					default:
						break;
				}
			},
			/**
			 * 歌曲播放模式
			 */
			playMode: function() {
				switch (this.mode) {
					case "iconfont icon-loop":
						this.mode = "iconfont icon-single"

						break;
					case "iconfont icon-single":
						this.mode = "iconfont icon-random"
						break;
					case "iconfont icon-random":
						this.mode = "iconfont icon-loop"
						break;
					default:
						break;
				}
			},
			/*
			 *弹出弹窗
			 */
			showPopup() {
				// 通过组件定义的ref调用uni-popup方法 ,如果传入参数 ，type 属性将失效 ，仅支持 ['top','left','bottom','right','center']
				this.$refs.popup.open('bottom')
				// uni.showActionSheet({
				// 	itemList: this.songlist,
				// 	success: function (res) {
				// 		console.log('选中了第' + (res.tapIndex + 1) + '个按钮');
				// 	},
				// 	fail: function (res) {
				// 		console.log(res.errMsg);
				// 	}
				// });
			},
			/**
			 * 在歌单中删除此歌曲
			 */
			deleteThis: function(id) {
				this.pause();
				this._audioContext.destroy();
				var index = -1;
				var nextSong = 0;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				nextSong = this.songlist[index + 1];
				this.ids.splice(i, 1);
				this.songlist.splice(i, 1);

				this.thisSong = nextSong;
				this.lrcshow();
				//播放器重置
				this.currentTime = 0;
				this._isChanging = false;
				this._audioContext = null;
				this.createAudio();

			},
			/**
			 * 播放制定音乐
			 */
			playThis: function(id) {
				this.pause();
				this._audioContext.destroy();
				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				this.thisSong = this.songlist[i];
				this.lrcshow();
				//播放器重置
				this.currentTime = 0;
				this._isChanging = false;
				this._audioContext = null;
				this.createAudio();
			}



		},

		components: {
			musichead
		},
	}
</script>

<style>
	.play {
		overflow: hidden;
	}

	.music-name {
		display: flex;
		position: relative;
		text-align: center;
		justify-content: center;
		color: white;
		font-size: 45rpx;
		height: 60rpx;
		width: 100%;
		line-height: 60rpx;
	}

	.music-artist {
		color: #c3c7ca;
		display: flex;
		position: relative;
		text-align: center;
		justify-content: center;
		font-size: 35rpx;
		height: 40rpx;
		width: 100%;
		line-height: 40rpx;
	}

	.play-box {
		width: 90%;
		height: 800rpx;
		position: relative;
		margin: 20rpx auto;
	}

	/* 唱片 */
	.music-play {
		width: 580rpx;
		height: 580rpx;
		background-image: url(../../static/disc.png);
		background-size: cover;
		margin: 110rpx auto 44rpx auto;
		position: relative;
	}

	.music-play image {
		width: 380rpx;
		height: 380rpx;
		border-radius: 50%;
		position: absolute;
		left: 0;
		top: 0;
		right: 0;
		bottom: 0;
		margin: auto;
		animation: discRotation 10s linear infinite;
		/* animation-play-state:var(--isRotation); */
	}

	.music-play-pause {
		animation-play-state: paused !important;
	}

	.music-play text {
		width: 100rpx;
		height: 100rpx;
		font-size: 100rpx;
		position: absolute;
		left: 0;
		top: 0;
		right: 0;
		bottom: 0;
		margin: auto;
		color: white;
	}

	.music-play view {
		position: absolute;
		width: 170rpx;
		height: 266rpx;
		left: 90rpx;
		right: 0;
		top: -80rpx;
		margin: auto;
		background: url(../../static/needle.png);
		background-size: cover;
	}

	@keyframes discRotation {
		from {
			transform: rotate(0deg);
		}

		to {
			transform: rotate(360deg);
		}
	}

	/* 歌词 */
	.lrcbox view {
		text-align: center;
		color: lightgray;
		font-size: 35rpx;
		line-height: 60rpx;
		min-height: 60rpx;
	}

	/* #67975a */
	.lrcShow {
		color: white !important;
		font-size: 38rpx !important;
	}

	.lrcbox scroll-view {
		width: 100%;
		height: 100%;
	}

	/* 底部按钮 */
	.btnbox {
		display: flex;
		width: 100%;
		height: 10%;
		position: absolute;
		bottom: 3%;
		text-align: center;
		justify-content: center;
		align-items: center;
	}

	.btnbox text {
		font-size: 100rpx;
		margin: 0 25rpx;
		color: white;
	}

	.btnbox .small {
		font-size: 80rpx;
	}


	/* 进度条 */
	.timebox {
		display: flex;
		width: 90%;
		height: 50rpx;
		position: absolute;
		left: 5%;
		bottom: 15%;

	}

	.timebox view {
		float: left;
		text-align: center;
		color: white;
	}

	.timebox .start_time {
		width: 20%;
	}

	.timebox .end_time {
		width: 20%;
	}

	.timebox slider {
		width: 60%;
		float: left;
		display: block;
		margin: 0;
	}

	/*popup*/

	uni-popup {
		height: 600rpx;
		overflow: hidden;
		width: 100vw;
	}

	.popup-content {
		background-color: whitesmoke;
		display: flex;
		width: 100%;
		height: 700rpx;
		/* overflow-x: hidden; */
		border-radius: 50rpx;
		/* 		padding: 50rpx auto; */
		position: relative;
	}

	.popup-top {
		display: flex;
		margin: 20rpx;
		width: 100%;
		height: 100rpx;
		line-height: 100rpx;
		margin-left: 8%;


	}

	.popup-top text:nth-child(1) {

		font-size: 40rpx;
		font-weight: bold;
		white-space: nowrap;
	}

	.popup-line {
		height: 0rpx;
		width: 90%;
		border: 1px solid #808080;
	}

	.popup-content scroll-view {
		/* 	display: flex; */
		/* position: relative; */

		border-top: 1px solid #808080;
		position: absolute;
		bottom: 0;
		height: 75%;
		width: 90%;
		margin-left: 5%;
		padding: 20rpx 10rpx;
	}

	.popup-item {
		display: flex;
		margin: 0 30rpx 70rpx 44rpx;
		align-items: center;
		position: relative;
		white-space: nowrap;
	}

	.popup-item-song {
		flex: 1;
		height: 100%;
		line-height: 40rpx;
		width: 70vw;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.popup-item-song text:nth-child(1) {
		color: black;
		font-size: 30rpx;
	}

	.popup-item-song text:nth-child(2) {
		color: #808080;
		font-size: 25rpx;
	}

	/* 	.popup-item view:nth-child(3) {
		font-size: 22rpx;
		color: #a2a2a2;
		width: 70vw;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		position: absolute;
		top: 45rpx;
		left: 56rpx;
	} */
</style>
