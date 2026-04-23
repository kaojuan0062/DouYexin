<template>
	<view class="footermusic" :style="{bottom:bottom}">
		<view class="footer-left" @tap="handleToDetail(thisSong.id)">
			<image :src="thisSong.picurl"></image>
			<view>
				<text>{{thisSong.name}}</text>
			</view>
		</view>
		<view class="footer-right">
			<text @tap="playFunc()" :class="playicon"></text>
			<text @tap="showPopup" class="iconfont icon-playlist"></text>
		</view>
		<!-- <audio ref="audio" :src="curSong.url"></audio> -->

		<!-- 底部弹窗播放列表 -->
		<view>
		<uni-popup ref="popup" type="bottom">

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
						<text @tap.stop="deleteThis(item.id)" class="iconfont icon-cancel"></text>
					</view>
				</scroll-view>
			</view>
		</uni-popup>
		</view>
	</view>
</template>

<script>
	import {
		getThisSong,
		getSongs
	} from '../../common/api.js'
	import {
		mapState,
		mapMutations,
		mapActions
	} from 'vuex'
	import '../../static/iconfont/iconfont.css'
	export default {
		name: "footermusic",
		props: ['bottom'],
		data() {
			return {
				//playImage: "iconfont icon-play",
			};
		},
		computed: {
			...mapState(['thisSong', 'ids', 'songlist', 'timeStr', 'innerAudioContext', 'isPlaying', 'isPlayEnd',
				'currentTime', 'duration'
			]),
			playicon(){
				if(this.isPlaying){
					return "iconfont icon-play";
				}else{
					return "iconfont icon-zanting"
				}
				//return "iconfont icon-zanting"
			}

		},
		mounted() {
			//console.log("audio标签"+JSON.stringify( this.$refs))
			console.log("底部组件+" + JSON.stringify(this.thisSong))
			this.setThisSong(this.thisSong)
		},
		beforeDestroy() {
			this.setThisSong(this.thisSong);
			this.setSonglist(this.songlist);
			this.setCurrentTime(this.currentTime);
			this.setIsPlaying(this.isPlaying)
			this.setIds(this.ids);
		},
		methods: {
			...mapMutations(['setIsPlaying', 'setThisSong', 'setSonglist', 'setCurrentTime', 'setDuration', 'setIds',
				'setMusicUrl', 'setIsChanging', 'setTimeStr'
			]),
			...mapActions(['play', 'pause', 'stop', 'onchanging', 'doChange']),
			handleToDetail(sid) {
				//this.setThisSong(this.thisSong);
				this.setSonglist(this.songlist);
				this.setCurrentTime(this.currentTime);
				this.setIsPlaying(this.isPlaying)
				this.setIds(this.ids);
				uni.navigateTo({
					url: '/pages/play/play?songId=' + sid +
						'&ids=' + this.ids,
				})
			},
			playFunc() {
				if (this.isPlaying) {
					//this.playImage = "iconfont icon-zanting";
					this.pause();
				} else {
					//this.playImage = "iconfont icon-play";
					this.play();
				}
			},

			/*
			 *弹出弹窗
			 */
			showPopup() {
				this.$refs.popup.open('bottom')
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
				var index = -1;
				var nextSong = 0;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				if (this.thisSong.id == id) {
					this.nextSong(id);
				}
				var afterIds = this.ids;
				afterIds.splice(i, 1);
				var afterSonglist = this.songlist;
				afterSonglist.splice(i, 1);
				console.log("删除当前歌单歌曲后歌单长度" + afterIds.length)
				
				this.setIds(afterIds)
				this.setSonglist(afterSonglist)

			},
			nextSong: function(id) {
				//var preSrc = this.innerAudioContext.src;
				//this.pause(); //先暂停，再切换
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
				} else {
					this.thisId = this.ids[index + 1];
				}
				console.log("这一首" + this.innerAudioContext.src);
				this.playThis(this.thisId)
				// getThisSong(this.thisId).then(res => {
				// 	if (res != null && res != undefined) {
				// 		this.thisSong = res;
				// 		console.log("下一首id" + this.thisSong.url)
				// 		this.createAudio();
				// 		console.log("下一首" + this.innerAudioContext.src + "；开始时间" + this.innerAudioContext
				// 			.currentTime);
				// 		this.setIsChanging(false);
				// 	}
				// })

			},
			
			/**
			 * 播放制定音乐
			 */
			playThis: function(id) {
				this.pause();

				var index = -1;
				for (var i = 0; i < this.ids.length; i++) {
					if (id == this.ids[i]) {
						index = i;
						break;
					}
				}
				this.setThisSong(this.songlist[index]);
				//this.lrcshow();
				//播放器重置
				console.log("指定切换" + this.thisSong.name)
				//this.lrcshow();
				this.setCurrentTime(0);
				this.innerAudioContext.seek(0);
				this.currentTimeStr = '00:00';
				//this.setTimeStr("00:00");
				console.log("开始时间" + this.innerAudioContext.currentTime);

				this.createAudio();
				this.setIsChanging(false);
				this.play()
				this.$refs.popup.close();
			},

			// 音乐播放器
			createAudio() {
				this.setMusicUrl(this.thisSong)
				this.innerAudioContext.onTimeUpdate((e) => {
					if (this.isChanging === true) {
						return;
					}
					this.setCurrentTime(this.innerAudioContext.currentTime || 0);
				});
				this.innerAudioContext.onEnded(() => {

					this.setCurrentTime(0)
					this.changeMusic();
				});
				this.innerAudioContext.onError(res => {
					console.log("播放错误")
					// console.log(res.errMsg);
					// console.log(res.errCode);
				});
			},
			/**
			 * 歌曲播完后切换
			 */
			changeMusic: function() {
				this.pause();//暂停
				//重置歌词
				this.top = 0;
				this.lrcIndex = -1;
				switch (this.mode) {
					case "iconfont icon-loop":      //顺序播放
						this.nextSong(this.thisSong.id);
						break;
					case "iconfont icon-single":    //单曲循环
						//播放器重置
						this.setIsChanging(true);
						this.setCurrentTime(0);
						this.innerAudioContext.seek(0);
						this.currentTimeStr = '00:00';
						this.createAudio();
						this.setIsChanging(false);
						break;
					case "iconfont icon-random":    //随机播放
						var index = Math.floor(Math.random() * (this.ids.length - 1));
						getThisSong(this.ids[index]).then(res => {
							this.thisSong = res;
							console.log("随机模式" + this.thisSong.url)
							this.lrcshow();
							this.setCurrentTime(0);
							this.innerAudioContext.seek(0);
							this.currentTimeStr = '00:00';
							console.log("下一首" + this.innerAudioContext.src + "；开始时间" + this.innerAudioContext.currentTime);
							this.createAudio();
							this.setIsChanging(false);
						})
						break;
					default:
						break;
				}
			},
			

		}
	}
</script>

<style lang="scss" scoped>
	.footermusic {
		width: 100%;
		height: 120rpx;
		position: fixed;
		// bottom: 220rpx;
		border-top: 1rpx solid #999;
		display: flex;
		justify-content: space-between;
		background-color: #fff;
		z-index: 99;
		opacity: 1;	
		.footer-left {
			//float: left;
			//left: 15rpx;
			width: 70%;
			height: 100%;
			display: flex;
			padding: 15rpx;
			image {
				width: 90rpx;
				height: 90rpx;
				border-radius: 50%;
			}

			text {
				height: 90rpx;
				line-height: 90rpx;
				margin-left: 30rpx;
				width: 70%;
				overflow: hidden;
				text-overflow: ellipsis;
				white-space: nowrap;
			}
		}

		.footer-right {
			width: 20%;
			height: 100%;
			display: flex;
			//align-items: center;
			position: fixed;
			//float: right;
			right: 15rpx;
			padding: 15rpx;
			//justify-content: space-between;
			text {
				height: 90rpx;
				line-height: 90rpx;
				font-size: 50rpx;
				color: #000;
				margin-left: 20rpx;
			}
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

	}
</style>
