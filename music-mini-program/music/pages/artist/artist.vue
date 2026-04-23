<template>
	<view class="artist">
		<view class="artistbg" :style="{backgroundImage:'url('+artist.picurl+')'}"></view>
		<musichead title="歌手" :icon="true" color="white"></musichead>
		<view class="container">
			<view class="artist-head">
				<view class="artist-head-name">
					{{artist.name}}
				</view>
				<view class="artist-head-desc">
					<text>{{artist.briefdesc}}</text>
				</view>

			</view>
			<!-- 判断是否是微信用户 -->
			<!-- #ifdef MP-WEIXIN -->
			<button v-show="isShow" class="list-share" open-type="share">
				<text class="iconfont icon-share">分享给微信好友</text>
			</button>
			<!-- #endif -->

			<view class="list-music">
				<view class="list-music-head" @tap="playTotal">
					<text class="iconfont icon-bofang"></text>
					<text>播放全部</text>
					<text>（共{{songlist.length}}首）</text>
				</view>
				
				<scroll-view scroll-y="true">
					<view class="list-music-item" v-for="(item,index) in songlist" :key="item.id"
						@tap="handleToDetail(item.id)">
						<view class="list-music-top">{{index+1}}</view>
						<view class="list-music-song">
							<view>{{item.name}}</view>
						</view>
						<view>
							{{item.artistName}}-{{item.name}}
						</view>
						<text class="iconfont icon-addToList" @tap.stop="openAddtoSlWindow(item.id)"></text>
					</view>
				</scroll-view>
			</view>
		</view>
		<addToSelflist :songid="addsongid" :atslShow="atslShow" @changeShowAddtoSl="changeShowAddtoSl"></addToSelflist> 
		<footermusic bottom="0rpx"></footermusic>
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import addToSelflist from '../../components/addToSelflist/addToSelflist.vue'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import {mapState,mapMutations,mapActions} from 'vuex'
	import {
		getArtistDetail,
		getSongsOfAritist
	} from '../../common/api.js'
	export default {
		data() {
			return {
				artistId: '',
				artist: {
					id: '',
					name: '',
					picurl: '',
					musicsize: '',
					briefdesc: ''
				},
				songIds: [],
				//songlist: [],
				isShow: true,
				atslShow:false,
				addsongid:''
			}
		},
		components: {
			musichead,
			addToSelflist,
			footermusic
		},
		computed:{
			...mapState(['ids','songlist','timeStr','innerAudioContext','isPlaying','isPlayEnd','currentTime','duration']),
		},
		onLoad(options) {
			console.log("artistid==", options.id)
			getArtistDetail(options.id).then(res => {
				if (res != null) {
					this.artist = res;
				}
			});
			getSongsOfAritist(options.id).then(res => {
				if (res != null) {
					this.setSonglist(res);
				}
			})

		},
		methods: {
			...mapMutations(['setSonglist','setCurrentTime','setDuration','setIds','setMusicUrl','setIsChanging','setTimeStr']),
			...mapActions(['play','pause','stop','onchanging','doChange']),
			handleToDetail(id) {
				console.log("歌曲id", id);
				for (var i = 0; i < this.songlist.length; i++) {
					this.songIds[i] = this.songlist[i].id;
				}
				this.setSonglist(this.songlist)
				uni.navigateTo({
					url: '/pages/play/play?songId=' + id +
						'&ids=' + this.songIds ,
				})
			},
			//加入歌单
			changeShowAddtoSl(isShow) { //组件传值
				this.atslShow = isShow
			},
			openAddtoSlWindow(songid) {
				this.atslShow = true;
				this.addsongid=songid
			},
			playTotal(){
				var first=this.songlist[0]
				console.log(first+"==="+JSON.stringify(this.songlist[0]))
				this.handleToDetail(first.id)
			}

		}
	}
</script>

<style scoped>
	.container{
		padding-bottom: 150rpx;
	}
	.artist{
		width: 100%;
		height: 100%;
	}
	/* 上半部分 */
	.artistbg {
		width: 100%;
		height: 60vh;
		position: fixed;
		background-size: cover;
		background-position: center 0;
		opacity: 0.5;
		filter: blur(1px);
		z-index: 0 !important;
		background-color: dark;
	}

	.artist-head {
		width: 100%;
		/* display: flex; */
		margin: 300rpx 30rpx 30rpx 0rpx;
		z-index: 1 !important;
		position: relative;
		/* color: white; */
	}

	.artist-head-name {
		width: 100%;
		height: 60rpx;
		line-height: 60rpx;
		text-align: left;
		font-weight: bold;
		font-size: 38rpx;
		white-space: nowrap;
		margin-left: 30rpx;
		letter-spacing: 5rpx;
		margin-bottom: 10rpx;

	}

	.artist-head-desc {	
		font-size: 25rpx;
		overflow: hidden;
		word-break: break-all;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 3;
		margin-left: 30rpx;
		margin-right: 30rpx;
		text-indent: 50rpx;
	
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
		margin-top: 30rpx;
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
</style>
