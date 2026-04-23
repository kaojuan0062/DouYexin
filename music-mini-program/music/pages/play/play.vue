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
							<view></view>
						</view>
					</swiper-item>
					<swiper-item class="lrcbox">
						<scroll-view scroll-y="false" :scroll-top="top" touch-action='none' cancelable='false'>
							<view v-for="(item,index) in lrcData" :key="index">
								<view :class="index==lrcIndex?'lrcShow':''">{{item[1]}}</view>
							</view>
						</scroll-view>
					</swiper-item>
				</swiper>
				<!-- 弹幕发送窗口 -->
				<uni-popup ref="danmuPopup" type="bottom">
					<view class="danmuPopup-bg">
						<input type="text" auto-focus="true" placeholder="发个弹幕" v-model="danmu.content" name="content" />
						<button class="btn-send" @tap="sendDanmu(thisSong.id)">发送</button>
					</view>
				</uni-popup>
				<view class="btnbox btnbox-top">
					<view class="danmu-btn" @tap="openInput">
						<text>发个弹幕</text>
					</view>
					<!-- 判断是否是微信用户 -->
					<!-- #ifdef MP-WEIXIN -->
					<button v-show="true" class="song-share" open-type="share">
						<text class="iconfont icon-share"></text>
					</button>
					<!-- #endif -->
					<!-- 添加到歌单 -->
					<text class="iconfont icon-add-bold" @tap="openAddtoSlWindow(thisSong.id)"></text>
					<!-- 收藏 -->
					<text :class="liked?'iconfont icon-liked':'iconfont icon-like'"
						@tap="addMylike(thisSong.id)"></text>
					<!-- 打开弹幕/取消弹幕-->
					<text :class="dmShow?'iconfont icon-danmu-open':'iconfont icon-danmu-close'" @tap="changeDanmu"></text>

				</view>
				<!-- 弹幕 -->
				<!-- 				<view class="dmGroup top ">
					<view class="dmItem">
						<view class="dm animation" :animation="animationData">

							<image class="dm-pic" :src="dm.userPic" mode="aspectFit"></image>
							<text class="dm-content">{{dm.content}}</text>

						</view>
					</view>
				</view> -->
				<!-- 进度条 -->
				<view class="timebox">
					<view class="start_time">{{currentTimeStr}}</view>
					<slider block-size="12" activeColor="#c4d39b" :min="0" :max="duration" @changing="onchanging"
						@change="onchange" :value="position">
					</slider>
					<view class="end_time">{{timeStr}}</view>
				</view>
				<!-- 播放按钮 -->
				<view class="btnbox btnbox-bottom">
					<text @tap="playMode" :class="mode" class="small"></text>
					<text @tap="preSong(thisSong.id)" class="iconfont icon-shangyishou"></text>
					<text @tap="playFunc()" :class="playicon"></text>
					<text @tap="nextSong(thisSong.id)" class="iconfont icon-xiayishou"></text>
					<text @tap="showPopup" class="iconfont icon-playlist small"></text>
				</view>
			</view>
		</view>
		<!-- 底部弹窗播放列表 -->
		<uni-popup ref="popup" type="bottom">

			<view class="popup-content">
				<view class="popup-top">
					<text>当前播放</text>
				</view>
				<scroll-view scroll-y="true">
					<view class="popup-item" v-for="(item,index) in songlist" :key="index">

						<view class="popup-item-song" @tap="playThis(item)">
							<text>{{item.name}}</text>

							<text>-{{item.artistName}}</text>
						</view>
						<text @tap.stop="deleteThis(item.id)" class="iconfont icon-cancel"></text>
					</view>
				</scroll-view>
			</view>
		</uni-popup>
		<!-- 弹幕 -->
		<danmu ref="danmu" :dmShow="dmShow"></danmu>
		<!-- 加入歌单 -->
		<addToSelflist :songid="addsongid" :atslShow="atslShow" @changeShowAddtoSl="changeShowAddtoSl"></addToSelflist>
		<login ref="login" :loginShow="loginShow" @changeloginShow="changeloginShow"></login>
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import danmu from '../../components/danmu/danmu.vue'
	import addToSelflist from '../../components/addToSelflist/addToSelflist.vue'
	import login from '../../components/login/login.vue'
	import {
		getThisSong,
		getSongs,
		createDanmu,
		getDanmus,
		addMylike,
		isLiked,
		cancelCollection
	} from '../../common/api.js'
	//const audioUrl = 'http://music.163.com/song/media/outer/url?id=65234'
	let thisthis = null;
	import {
		mapState,
		mapMutations,
		mapActions
	} from 'vuex'
	export default {

		data() {
			return {
				icon: true,
				//thisSong: {},
				lrcData: [],
				lrcIndex: -1,
				top: '',
				thisId: '',
				//ids: [],
				//mode: "iconfont icon-loop",
				playImage: "iconfont icon-play",
				//songlist: [],

				title: "innerAudioContext",
				// isPlaying: false,
				// isPlayEnd: false,
				// currentTime: 0,
				currentTimeStr: '00:00',
				// duration: 100,
				//timeStr: '00:00:00',

				danmu: {
					id: '',
					openid: '',
					sendTime: '',
					songId: '',
					status: 0,
					content: '',
					createDate: '',

				},
				userinfo: {},
				danmulist: [{
					id: '',
					openid: '',
					userPic: '',
					songId: '',
					sendTime: '',
					createTime: '',
					content: '',
					status: ''
				}],
				dm: {
					id: '',
					openid: '',
					userPic: '',
					songId: '',
					sendTime: '',
					createTime: '',
					content: '',
					status: ''
				},
				animationData: {},
				atslShow: false,
				addsongid: '',
				liked: false,
				loginShow: false,
				dmShow:true
			}
		},
		computed: {
			...mapState(['ids', 'songlist', 'timeStr', 'innerAudioContext', 'isPlaying', 'isPlayEnd', 'currentTime','thisSong',
				'duration', 'mode'
			]),
			//更新进度条位置
			position() {
				return this.isPlayEnd ? 0 : this.currentTime;
			},
			playicon(){
				if(this.isPlaying){
					return "iconfont icon-play";
				}else{
					return "iconfont icon-zanting"
				}
			}
		},
		onUnload() {
			this.setThisSong(this.thisSong);
			this.setSonglist(this.songlist);
			this.setCurrentTime(this.currentTime);
			this.setIsPlaying(this.isPlaying)
			this.setIds(this.ids);
			this.setMode(this.mode)
			this.animationData = {}
		},
		onShow() {
		 this.setTotal();
		},
		onLoad(options) {

			//播放器设置		
			thisthis = this;
			//console.log(options.songId+"=="+options.ids);
			//this.thisId = options.songId;
			//播放器设置
			// this._isChanging = false;
			// this._audioContext = null;
			this.userinfo = this.$store.state.userinfo
			if (typeof this.userinfo === 'string') {
				this.userinfo = JSON.parse(this.$store.state.userinfo)
			}
			//获取歌曲
			getThisSong(options.songId).then(res => {
				if (res != null) {
					this.setThisSong(res);
					this.lrcshow();
					this.createAudio();
					this.play()
				}
			})
			//获取当前歌曲列表
			this.setIds(options.ids.split(','));
			this.setMode(this.mode)
			//判断是否已收藏
			isLiked(this.userinfo.openid, options.songId).then(res => {
				if (res != null) {
					this.liked = res
					console.log("是否已收藏 "+res)
				}
			})
			this.setSonglist(this.songlist)
			
		},
		methods: {
			...mapMutations(['setIsPlaying', 'setThisSong', 'setSonglist', 'setCurrentTime', 'setDuration', 'setIds',
				'setMusicUrl', 'setIsChanging', 'setTimeStr', 'setMode'
			]),
			...mapActions(['play', 'pause', 'stop', 'onchanging', 'doChange']),
			playFunc() {
				if (this.isPlaying) {
					this.playImage = "iconfont icon-zanting";
					this.pause();
				} else {
					this.playImage = "iconfont icon-play";
					this.play();
				}
			},

			// 音乐播放器
			createAudio() {
				this.setMusicUrl(this.thisSong)
				//this.setCurrentTime(0);
				// //开始播放
				// this.innerAudioContext.play(); //执行播放
				// //设置播放状态
				//this.isPlaying(true)
				this.innerAudioContext.onTimeUpdate((e) => {
					if (this.isChanging === true) {
						this.top = 0;
						this.lrcIndex = -1;
						return;
					}
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
						this.top = (index - 5) * 30;

					}

					this.setCurrentTime(this.innerAudioContext.currentTime || 0);
					//this.setDuration(this.innerAudioContext.duration || 0);
					this.currentTimeStr = this.formatTime(this.currentTime);
					//进度条最大值
					//this.timeStr = this.formatSecond(this.duration);					

				});
				this.innerAudioContext.onEnded(() => {
					this.currentTimeStr = this.formatTime(0);
					this.changeMusic();
				});
				this.innerAudioContext.onError(res => {

					this.isRotation = "music-play-pause";
					console.log("播放错误")
				});
				//console.log(innerAudioContext);
				//console.log(this._audioContext)
				//return innerAudioContext;
			},
			onchange(e) {
				this.doChange(e);
				//将当前播放时长格式化，用于显示
				this.currentTimeStr = this.formatTime(this.currentTime)
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
			 * 歌词处理
			 */
			lrcshow: function() {
				var newLrclist = [];
				if (this.thisSong.lyric != null && this.thisSong.lyric != undefined) {
					var lrclist = this.thisSong.lyric.split('\n');
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
				//var preSrc = this.innerAudioContext.src;
				//this.pause(); //先暂停，再切换
				//this._isChanging = true;
				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				//当前位置
				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				if (index == this.ids.length - 1) {
					this.thisId = this.ids[0];
					this.playThis(this.songlist[0]);
				} else {
					this.thisId = this.ids[index + 1];
					this.playThis(this.songlist[index+1])
				}

			},
			/**
			 * 上一首
			 */
			preSong: function(id) {

				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				//当前位置
				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				if (index == 0) {
					this.thisId = this.ids[this.ids.length - 1];
					this.playThis(this.songlist[this.ids.length - 1])
				} else {
					this.thisId = this.ids[index-1];
					this.playThis(this.songlist[index-1])
				}
				
			},
			/**
			 * 歌曲播完后切换
			 */
			changeMusic: function() {
				this.pause(); //暂停
				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				switch (this.mode) {
					case "iconfont icon-loop": //顺序播放
						this.nextSong(this.thisSong.id);
						break;
					case "iconfont icon-single": //单曲循环
						//播放器重置
						this.setIsChanging(true);
						this.setCurrentTime(0);
						this.innerAudioContext.seek(0);
						this.currentTimeStr = '00:00';
						this.createAudio();
						this.setIsChanging(false);
						break;
					case "iconfont icon-random": //随机播放
						var index = Math.floor(Math.random() * (this.ids.length - 1));
						getThisSong(this.ids[index]).then(res => {
							this.setThisSong(res);
							console.log("随机模式" + this.thisSong.url)
							this.lrcshow();
							this.setCurrentTime(0);
							this.innerAudioContext.seek(0);
							this.currentTimeStr = '00:00';
							console.log("下一首" + this.innerAudioContext.src + "；开始时间" + this.innerAudioContext
								.currentTime);
							this.createAudio();
							this.setIsChanging(false);
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
						this.setMode("iconfont icon-single")

						break;
					case "iconfont icon-single":
						this.setMode("iconfont icon-random")
						break;
					case "iconfont icon-random":
						this.setMode("iconfont icon-loop")
						break;
					default:
						break;
				}
			},
			/*
			 *弹出弹窗
			 */
			showPopup() {
				this.setSonglist(this.songlist)
				// 通过组件定义的ref调用uni-popup方法 ,如果传入参数 ，type 属性将失效 ，仅支持 ['top','left','bottom','right','center']
				this.$refs.popup.open('bottom')
				
				// });
			},
			/**
			 * 在歌单中删除此歌曲
			 */
			deleteThis: function(id) {
				//如果删除的是最后一首
				if (this.ids.length == 1) {
					uni.showModal({
						title: '提示',
						content: '已是最后一首歌曲',
					})
					return
				
				}
				//this._audioContext.destroy();
				console.log("删除当前歌单歌曲前歌单长度" + this.ids.length)
				var index = -1;
				var nextSong = 0;
				// this.top = 0;
				// this.lrcIndex = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				if (this.thisSong.id == id) {
					this.nextSong(id);
				}
				// if (index == this.ids.length - 1) {
				// 	nextSong = this.songlist[0];
				// } else {
				// 	nextSong = this.songlist[index + 1];
				// }
				var afterIds = this.ids;
				afterIds.splice(i, 1);
				var afterSonglist = this.songlist;
				afterSonglist.splice(i, 1);
				this.setIds(afterIds)
				this.setSonglist(afterSonglist)
				console.log("删除当前歌单歌曲后歌单长度" + afterIds.length)
				//this.nextSong(id);
				// this.setIds(afterIds);
				// this.setSonglist(afterSonglist);
				// this.setThisSong(nextSong);
				// this.lrcshow();
				// //播放器重置
				// this.setCurrentTime(0);
				// this.setIsChanging(false);
				// this.createAudio();

			},
			setTotal(){
				this.setThisSong(this.thisSong);
				this.setSonglist(this.songlist);
				this.setCurrentTime(this.currentTime);
				this.setIsPlaying(this.isPlaying)
				this.setIds(this.ids);
				this.setMode(this.mode)
			},
			
			/**
			 * 播放制定音乐
			 */
			playThis: function(id) {
				this.pause();
				this.setThisSong(id);
				//this.lrcshow();
				//播放器重置
				console.log("指定切换" + this.thisSong.name)
				this.lrcshow();
				this.setCurrentTime(0);
				this.innerAudioContext.seek(0);
				this.currentTimeStr = '00:00';
				//this.setTimeStr("00:00");
				console.log("开始时间" + this.innerAudioContext.currentTime);
				this.setTotal();
				this.createAudio();
				this.setIsChanging(false);
				this.play()
				isLiked(this.userinfo.openid, this.thisSong.id).then(res => {
					if (res != null) {
						thisthis.liked = res
						console.log("是否已收藏 "+res)
					}
				})
				this.$refs.danmu.getDanmusAgain(thisthis.thisSong.id)
				this.$refs.popup.close();
			},
			//弹幕输入框
			openInput() {
				this.$refs.danmuPopup.open();
			},
			//发送弹幕
			sendDanmu: function(songid) {
				// this.userinfo = this.$store.state.userinfo
				// if (typeof this.userinfo === 'string') {
				// 	this.userinfo = JSON.parse(this.$store.state.userinfo)
				// }
				if (this.$store.state.checkSession==false) {				
					console.log("发送弹幕检查session为false")
					thisthis.loginShow = true;
					return
				} else {
					console.log("发送弹幕检查session为true")
					thisthis.loginShow = false;					
				}
				this.danmu.openid = this.userinfo.openid;
				this.danmu.songId = songid;
				this.danmu.sendTime = this.currentTime;
				console.log("发送的弹幕" + JSON.stringify(this.danmu))
				createDanmu(this.danmu).then(res => {
					let tosTitle = ''
					let tosIcon = 'fail'
					switch (res.data) {
						case 1: //合规
							tosTitle = "弹幕发送成功"
							tosIcon = "success"
							this.danmu.content = ""
							this.$refs.danmuPopup.close();
							this.$refs.danmu.getDanmusAgain(thisthis.thisSong.id)
							break;
						case 2:
							tosTitle = "弹幕内容违规"
							tosIcon = "error"
							break;
						case 3:
							tosTitle = "内容疑似违规"
							tosIcon = "error"
							break;
						case 4:
							//tosTitle="弹幕发送成功"
							tosIcon = "fail"
							break;
						default:
							break;

					}
					uni.showToast({
						title: tosTitle,
						icon: tosIcon,
						mask: true
					})
				})
			},
			
			//修改弹幕状态
			changeDanmu(){
				if(this.dmShow){
					this.dmShow=false
				}else{
					this.dmShow=true
				}
			},
			/**
			 * 加入歌单
			 * @param {Object} isShow
			 */
			changeShowAddtoSl(isShow) { //组件传值
				this.atslShow = isShow
			},
			openAddtoSlWindow(songid) {
				//判断是否登录
				if (this.$store.state.checkSession==false) {
					console.log("添加歌单检查session为false")
					this.loginShow = true;
					return
				} else {
					console.log("添加歌单检查session为true")
					this.loginShow = false;					
				}
				this.atslShow = true;
				this.addsongid = songid
				
			},
			changeloginShow(isShow) { //组件传值
				this.loginShow= isShow
			},
			/**
			 * 收藏歌曲
			 * @param {Object} songid
			 */
			addMylike(songid) {
				//判断是否登录
				if (this.$store.state.checkSession==false) {
					console.log("收藏检查session为false")
					this.loginShow = true;
					return
				} else {
					console.log("收藏检查session为true")
					this.loginShow = false;					
				}
				if (this.liked) {
					cancelCollection(this.userinfo.openid, songid).then(res => {
						if (res.statusCode == 200) {
							uni.showToast({
								title: "取消收藏成功",
								icon: "success",
								mask: true
							})
							this.liked=false
						}
					})
				} else {
					let mylike = {}
					mylike.songId = songid;
					mylike.openid = this.userinfo.openid
					addMylike(mylike).then(res => {
						if (res.statusCode == 200) {
							uni.showToast({
								title: "收藏歌曲成功",
								icon: "success",
								mask: true
							})
							this.liked=true
						} else {
							uni.showToast({
								title: "收藏歌曲失败",
								icon: "fail",
								mask: true
							})
						}
					})
				}
			},
		},
		// 页面隐藏的时候删除掉
		onHide() {
			//this.$refs.danmu.clerOn();
			//this.setSonglist(this.songlist)
			this.setTotal();
		},
		components: {
			musichead,
			danmu,
			addToSelflist,
			login
		},
	}
</script>

<style lang="scss" scoped>

	.play {
		overflow: hidden;
	}
	.music-top{
		view{
			overflow: hidden;
			//-o-text-overflow: ellipsis;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
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
		//color: #c3c7ca;
		color: #e0e0dd;
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
		height: 56vh;
		position: relative;
		margin: 20rpx auto;
	}

	/* 唱片 */
	.music-play {
		width: 580rpx;
		height: 580rpx;
		background-image: url(../../static/disc.png);
		background-size: cover;
		margin: 80rpx auto 44rpx auto;
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

	// .music-play text {
	// 	width: 100rpx;
	// 	height: 100rpx;
	// 	font-size: 100rpx;
	// 	position: absolute;
	// 	left: 0;
	// 	top: 0;
	// 	right: 0;
	// 	bottom: 0;
	// 	margin: auto;
	// 	color: white;
	// }

	.music-play view {
		position: absolute;
		width: 170rpx;
		height: 266rpx;
		left: 90rpx;
		right: 0;
		top: -80rpx;
		margin: auto;
		// background: url(../../static/needle.png);
		// background-size: cover;
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
		text-align: center;
		justify-content: center;
		align-items: center;
	}

	.btnbox-top {
		justify-content: space-evenly;
		bottom: 15%;
		color: white;

		.danmu-btn {
			font-size: 28rpx;
			padding: 5rpx;
			height: 60rpx;
			width: 300rpx;
			border-radius: 100rpx;
			display: flex;
			justify-content: center;
			align-items: center;
			background-color: rgba(255, 255, 255, 0.12);
			margin-right: 50rpx;
		}

		.iconfont {
			font-size: 50rpx;
		}
	}

	.btnbox-bottom {
		bottom: 3%;
	}

	.btnbox-bottom text {
		font-size: 80rpx;
		margin: 0 25rpx;
		color: white;
	}
	.song-share{
		color: white;
		background-color: transparent;
		margin: 0rpx;
		padding: 0rpx;
	}
	.song-share::after{
			border: none;		
	}

	.btnbox-bottom .small {
		font-size: 60rpx;
	}

	/*弹幕输入框*/
	.danmuPopup-bg {
		background-color: #fff;
		display: flex;
		align-items: center;
		//justify-content: space-between;
		height: 120rpx;

		input {
			width: 60%;
			position: fixed;
			left: 30rpx;
			height: 60rpx;
			line-height: 80rpx;
			border-radius: 15rpx;
			border: 1rpx solid #808080;
			font-size: 32rpx;
		}

	}

	.btn-send {
		width: 190rpx;
		height: 60rpx;
		line-height: 60rpx;
		border-radius: 30rpx;
		font-size: 32rpx;
		position: fixed;
		right: 30rpx;
		color: white;
		background-color: #658257;
		align-items: center;
		justify-content: center;
	}


	/* 进度条 */
	.timebox {
		display: flex;
		width: 90%;
		height: 50rpx;
		position: absolute;
		left: 5%;
		bottom: 12%;

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

	//弹幕
	.dmGroup {
		position: fixed;
		top: 25rpx;
		left: -50%;
		z-index: 10;
		white-space: nowrap;
		height: 60rpx;
		//animation: mymove 15s linear forwards infinite;
	}

	.dmGroup.top {
		top: 125rpx;
		height: 64rpx;

	}

	.dmGroup.mid {
		height: 64rpx;
		top: 125rpx;
	}

	.dmGroup.btm {
		height: 60rpx;
		top: 260rpx;
	}

	.dm {
		display: inline-flex;
		margin-right: 60rpx;
		white-space: nowrap;
		justify-content: center;
		align-items: center;
		align-content: center;
		color: white;
		background-color: rgba(255, 255, 255, 0.4);
		border-radius: 30rpx;
		height: 60rpx;
		line-height: 60rpx;
		padding: 5rpx 10rpx;

		.dm-pic {
			width: 50rpx;
			height: 50rpx;
			border-radius: 50%;
			margin-right: 10rpx;
		}

		.dm-content {
			font-size: 28rpx;
			line-height: 50rpx;
			height: 50rpx;
		}
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
