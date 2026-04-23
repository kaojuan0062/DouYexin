<template>
	<view class="list">
		<view class="fixbg" :style="{backgroundImage:'url('+playlist.coverimgurl+')'}"></view>
		<musichead title="歌单" :icon="true" color="white"></musichead>
		<addToSelflist :songid="addsongid" :atslShow="atslShow" @changeShowAddtoSl="changeShowAddtoSl"></addToSelflist>
		<view class="container">
			<view class="list-head">
				<view class="list-head-img">
					<image :src="playlist.coverimgurl"></image>
					<text class="iconfont icon-bofang"> {{playlist.playCount|formatCount}}</text>
				</view>
				<view class="list-head-text">
					<view>
						{{playlist.name}}
					</view>
					<view>
						<image :src="playlist.creatorAvatarurl"></image>
						<text>{{playlist.creatorNickname}}</text>
					</view>
					<view>
						{{playlist.description}}
					</view>
				</view>

			</view>
			<!-- 判断是否是微信用户 -->
			<!-- #ifdef MP-WEIXIN -->
			<button v-show="isShow" class="list-share" open-type="share">
				<text class="iconfont icon-share">分享给微信好友</text>
			</button>
			<!-- #endif -->

			<view class="list-music">
				<view @tap="playTotal" class="list-music-head">
					<text class="iconfont icon-bofang"></text>
					<text>播放全部</text>
					<text>（共{{songlist.length}}首）</text>
				</view>
				<scroll-view scroll-y="true">
					<view class="list-music-item" v-for="(item,index) in songlist" :key="index"
						@tap="handleToDetail(item.id)">

						<view class="list-music-top">{{index+1}}</view>
						<view class="list-music-song">
							<view>{{item.name}}</view>
						</view>
						<view>
							<!-- <image v-if="privileges[index].flag>60 && privileges[index].flag<70"
								src="../../static/VIP.png"></image>
							<image v-if="privileges[index].maxbr==999000" src="../../static/VIP.png"></image> -->
							{{item.artistName}}-{{item.name}}
						</view>
						<text class="iconfont icon-addToList" @tap.stop="openAddtoSlWindow(item.id)"></text>
					</view>
				</scroll-view>
			</view>
		</view>
		<footermusic bottom="0rpx"></footermusic>
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import addToSelflist from '../../components/addToSelflist/addToSelflist.vue'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import {
		mapState,
		mapMutations,
		mapActions
	} from 'vuex'
	import {
		playlist,
		getSongs,
		getTopTrackcounts,
		getMylike
	} from '../../common/api.js'
	export default {
		data() {
			return {
				plistId: '',
				playlist: {
					// coverImgUrl: '',
					// creator: {
					// 	avatarUrl: ''
					// },
					// trackCount: ''
				},
				songIds: [],
				isShow: true,
				atslShow: false,
				addsongid: ''
			}
		},
		computed: {
			...mapState(['ids', 'songlist', 'timeStr', 'innerAudioContext', 'isPlaying', 'isPlayEnd', 'currentTime',
				'duration'
			]),
		},
		components: {
			musichead,
			addToSelflist,
			footermusic
		},
		onLoad(options) {
			this.plistId = options.id;
			playlist(this.plistId).then(res => {
				//this.plistId = options.id;
				if (res != null) {
					this.playlist = res;
				}
			})
			console.log("listid", options.id)
			if (this.plistId == 'topTrack') {
				getTopTrackcounts().then(res => {
					if (res != null) {
						this.setSonglist(res);
					}
				})
			}
			
			 else {
				getSongs(this.plistId).then(res => {
					if (res != null) {
						//this.songlist = res;
						this.setSonglist(res);
						//console.log("list页面存入的list==",uni.getStorageSync('songlist'))
					}
				})
			}


		},
		methods: {
			...mapMutations(['setSonglist', 'setCurrentTime', 'setDuration', 'setIds', 'setMusicUrl', 'setIsChanging',
				'setTimeStr'
			]),
			...mapActions(['play', 'pause', 'stop', 'onchanging', 'doChange']),
			handleToDetail(id) {
				console.log("歌曲id", id);
				for (var i = 0; i < this.songlist.length; i++) {
					this.songIds[i] = this.songlist[i].id;
				}
				this.setSonglist(this.songlist)
				uni.navigateTo({
					url: '/pages/play/play?songId=' + id +
						'&ids=' + this.songIds +
						'&pId=' + this.plistId,
				})
			},
			//加入歌单
			changeShowAddtoSl(isShow) { //组件传值
				this.atslShow = isShow
			},
			openAddtoSlWindow(songid) {
				this.atslShow = true;
				this.addsongid = songid
			},
			//播放全部
			playTotal(){
				var first=this.songlist[0]
				console.log(first+"==="+JSON.stringify(this.songlist[0]))
				this.handleToDetail(first.id)
			}

		}
	}
</script>

<style>
	.container{
		padding-bottom: 125rpx;
	}
	/* 上半部分 */
	.list-head {
		display: flex;
		margin: 30rpx;
	}

	.list-head-img {
		width: 265rpx;
		height: 256rpx;
		border-radius: 15rpx;
		margin-right: 40rpx;
		overflow: hidden;
		position: relative;
	}

	.list-head-img image {
		width: 100%;
		height: 100%;
	}

	.list-head-img text {
		position: absolute;
		font-size: 26rpx;
		right: 8px;
		top: 8px;
		color: white;
	}

	.list-head-text {
		flex: 1;
		font-size: 24rpx;
		color: white;
		z-index: 1;
	}

	.list-head-text image {
		width: 52rpx;
		height: 52rpx;
		border-radius: 50%;
	}

	.list-head-text view:nth-child(1) {
		font-size: 34rpx;
		color: white;
	}

	.list-head-text view:nth-child(2) {
		display: flex;
		align-items: center;
		margin: 30rpx 0;
	}

	.list-head-text view:nth-child(2) text {
		margin-left: 15rpx;
	}

	.list-head-text view:nth-child(3) {
		line-height: 38rpx;
	}

	.list-share {
		width: 380rpx;
		height: 72rpx;
		margin: 0 auto;
		background-color: rgba(0, 0, 0, 0.4);
		text-align: center;
		line-height: 72rpx;
		font-size: 16rpx;
		color: white;
		border-radius: 23rpx;
	}

	/* 	歌单列表 */
	/* 	播放全部 */
	.list-music {
		background: white;
		border-radius: 50rpx 50rpx 0 0;
		overflow: hidden;
		margin-top: 45rpx;
		position: relative;
		z-index: 2;
	}

	.list-music scroll-view {

		height: 800rpx;
	}

	.list-music-head {
		height: 58rpx;
		line-height: 58rpx;
		margin: 30rpx 30rpx 70rpx 30rpx;
	}

	.list-music-head text:nth-child(1) {
		font-size: 40rpx;

	}

	.list-music-head text:nth-child(2) {
		font-size: 34rpx;
		margin: 0 10rpx 0 25rpx;

	}

	.list-music-head text:nth-child(3) {
		font-size: 28rpx;
		color: #b2b2b2;
	}

	//歌曲
	.list-music-item {
		display: flex;
		margin: 0 30rpx 70rpx 44rpx;
		align-items: center;
		position: relative;
	}

	.list-music-top {
		width: 56rpx;
		font-size: 28rpx;
		color: #979797;

	}

	.list-music-song {
		flex: 1;
		line-height: 40rpx;

	}

	.list-music-song view {
		font-size: 30rpx;
		width: 70vw;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.list-music-item view:nth-child(3) {
		font-size: 22rpx;
		color: #a2a2a2;
		width: 70vw;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		position: absolute;
		top: 45rpx;
		left: 56rpx;
	}

	.list-music-item image {
		width: 34rpx;
		height: 22rpx;
		margin-right: 10rpx;
	}

	.list-music-item text {
		width: 50rpx;
		height: 100%;
		align-items: center;
		z-index: 50;
	}
</style>
