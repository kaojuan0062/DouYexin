<template>
	<view class="index">
		<!-- <musichead title="网易云音乐" :icon="true"></musichead> -->
		<view class="container">
			<!-- =====搜索歌曲========= -->


			<view class="index-search">
				<view class="index-search-input" @tap="handleToSearch">
					<text class="iconfont icon-search"></text>
					<text>搜索歌曲</text>
				</view>
			</view>

			<!-- =======轮播图======= -->
			<view class="banners">
				<!-- rgb为背景颜色；banner效果图 -->
				<swiper class="banner-swiper" indicator-dots="true" indicator-color="rgb(255, 255, 255,0.5)"
					indicator-active-color="#ff372b" autoplay="true" duration="500" interval="3000" circular="true">
					<swiper-item v-for="(item,index) in bannerList" :key="index" class="banner-swiper-item">
						<image :src="item.imageurl" mode="widthFix"></image>
						<!-- <view class="banner-swiper-item-tag">{{item.typeTitle}}</view> -->
					</swiper-item>
				</swiper>
			</view>
			<!-- ======热门歌手====== -->
			<view class="artists">
				<view class="column-top">
					<text>热门歌手</text>
					<text @tap="handleToArtistlist" class="iconfont icon-more"></text>
				</view>
				<view class="artist-list">
					<scroll-view scroll-x="true">

						<view class="artist-list-item" v-for="(item,index) in artistList" :key="index"
							@tap="handleToArtist(item.id)">
							<image :src="item.picurl" mode="heightFix"></image>
							<view>{{item.name}}</view>
						</view>
					</scroll-view>
				</view>
			</view>
			<!-- =======排行榜======== -->
			<view class="rankList">
				<view class="column-top">
					<text>排行榜</text>
					<text class="iconfont icon-more" @tap="handleToPlaylists"></text>
				</view>
				<view class="rank">
					<scroll-view scroll-x="true">
						<view class="rank-item" key="topTrack">
							<view class="rank-item-name" @tap="handleToList('topTrack')">
								播放量排行榜
								<text class="iconfont icon-right"></text>
							</view>
							<view class="rank-item-content" v-for="(song,songIndex) in topTractcounts" :key="songIndex"
								@tap="handleToDetail(999,song.id)">
								<image :src="song.picurl"></image>
								<view>{{songIndex+1}}</view>
								<view>{{song.name}}</view>
								<view>-{{song.artistName}}</view>
								<text class="iconfont icon-playCircle"></text>

							</view>
						</view>
						<view class="rank-item" v-for="(item,rankIndex) in topList" :key="item.id">
							<view class="rank-item-name" @tap="handleToList(item.id)">
								{{item.name}}
								<text class="iconfont icon-right"></text>
							</view>
							<view class="rank-item-content" v-for="(song,songIndex) in playlists[rankIndex]"
								:key="songIndex" @tap="handleToDetail(rankIndex,song.id)">
								<image :src="song.picurl"></image>
								<view>{{songIndex+1}}</view>
								<view>{{song.name}}</view>
								<view>-{{song.artistName}}</view>
								<!-- 							<text>{{songIndex+1}}</text>
								<text>{{song.ar[0].name}}</text>
								<text>-{{song.name}}</text> -->
								<text class="iconfont icon-playCircle"></text>

							</view>
						</view>
					</scroll-view>
				</view>
			</view>


			<!-- 改！！！！！！！！！！！！！！！=====渲染列表=========== -->
			<!-- <view class="index-list">
				<view class="index-list-item" v-for="(item,index) in topList" :key="item.id"
					@tap="handleToList(item.id)">
					<view class="index-list-item-img">
						<image :src="item.coverImgUrl"></image>
						<text>{{item.updateFrequency}}</text>
					</view>
					<view class="index-list-item-text">
						<view v-for="(musicItem,index) in item.tracks" :key="index">
							{{index+1}}.{{musicItem.first}}-{{musicItem.second}}
						</view>
					</view>
				</view>
			</view> -->
		</view>
		<footermusic bottom="125rpx"></footermusic>
		<tabbar :selected="selected"></tabbar>


	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import tabbar from '../../components/tabbar/tabbar.vue'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import {
		mapState,
		mapMutations,
		mapActions
	} from 'vuex'
	import {
		topList,
		getBanner,
		getArtists,
		getSongs,
		topListAndSong,
		isExist,
		getUser,
		playlist,
		getTopTrackcounts

	} from '../../common/api.js'
	import {
		baseUrl
	} from '../../common/config.js'
	let thisthis = null;
	export default {
		data() {
			return {
				bannerList: [],
				artistList: [],
				topList: [],
				playlists: [],
				totalLists: [],
				selected: 0,
				totalTopTrackocunts: [],
				topTractcounts: [],

			}
		},
		components: {
			musichead,
			tabbar,
			footermusic,
		},
		computed: {
			...mapState(['ids', 'songlist', 'timeStr', 'innerAudioContext', 'isPlaying', 'isPlayEnd', 'currentTime','thisSong',
				'duration', 'mode'
			]),
		},
		onLoad() {

			thisthis = this;
			//topListAndSong();
			topList().then(res => {
				if (res != null) {
					this.topList = res;
					//console.log("topList().then()===", res);
					this.initPlaylist();
				}
			});
			//获取轮播图
			getBanner().then(res => {
				if (res != null) {
					this.bannerList = res;
					//console.log("getBanner().then()===", this.bannerList)
				}
			});
			//获取歌手列表
			getArtists().then(res => {
				if (res != null) {
					this.artistList = res;
					this.artistList.length = 6;
					//console.log("getArtist().then()===", this.artistList)
				}
			});
			//获取本地播放量前20
			getTopTrackcounts().then(res => {
				if (res != null) {
					this.totalTopTrackocunts = res;
					this.topTractcounts = res.slice(0, 5);
				}
			})
			//thisthis.$forceUpdate()
			//获取登录信息
			// if(this.$store.state.checkSession==true){
			// 	if(isExist())
			// }

		},
		onNavigationBarSearchInputClicked() {
			console.log("在这里指定我们的跳转路径")
			uni.navigateTo({
				url: '../search/search'
			});
		},
		methods: {
			...mapMutations(['setIsPlaying', 'setThisSong', 'setSonglist', 'setCurrentTime', 'setDuration', 'setIds',
				'setMusicUrl', 'setIsChanging', 'setTimeStr', 'setMode'
			]),
			...mapActions(['play', 'pause', 'stop', 'onchanging', 'doChange']),

			initPlaylist() {
				//console.log("initPlaylist()触发==", this.topList);
				for (let i = 0; i < this.topList.length; i++) {
					//console.log("FOR of initPlaylist()", this.topList[i].id)
					getSongs(this.topList[i].id).then(res => {
						if (res != null) {
							var array = res;
							thisthis.totalLists.push(array);
							thisthis.playlists.push(array.slice(0, 5));

							//thisthis.$set(thisthis.totalLists, i, res);
							//console.log("initPlaylist().then()===", thisthis.playlists[i])
						}
					});

				}
				// console.log("ALLLinitPlaylist().then()===", thisthis.playlists[1].value)
				// console.log("playlist的长度", this.playlists.length);
				// });

			},
			handleToSearch() {
				console.log("点击搜索框")
				uni.navigateTo({
					url: '../search/search'
				});
			},
			handleToList(id) {
				console.log(id)
				uni.navigateTo({
					url: '/pages/list/list?id=' + id,
				});
			},
			handleToPlaylists() {
				uni.navigateTo({
					url: '/pages/playlists/playlists',
				});
			},
			handleToArtistlist() {
				uni.navigateTo({
					url: '/pages/artistlist/artistlist',
				});
			},
			handleToArtist(id) {
				console.log(id)
				uni.navigateTo({
					url: '/pages/artist/artist?id=' + id,
				});
			},
			handleToDetail(index, sid) {
				let songIds = []
				let songlist = []
				if (index < 999) { //官方歌单或歌手
					songlist = this.totalLists[index]
					this.setSonglist(this.totalLists[index]);
				} else if (index == 999) { //本地播放量
					console.log("total的长度", this.totalTopTrackocunts);
					songlist = this.totalTopTrackocunts
					this.setSonglist(this.totalTopTrackocunts);
				}
				for (var i = 0; i < songlist.length; i++) {
					songIds[i] = songlist[i].id;
				}
				this.setTotal();
				
				//this.setSonglist( this.totalLists[index]);
				uni.navigateTo({
					url: '/pages/play/play?songId=' + sid +
						'&ids=' + songIds,
				})
			},
			setTotal(){
				this.setThisSong(this.thisSong);
				this.setSonglist(this.songlist);
				this.setCurrentTime(this.currentTime);
				this.setIsPlaying(this.isPlaying)
				this.setIds(this.ids);
				this.setMode(this.mode)
			}


		}
	}
</script>

<style lang="scss" scoped>
	.index-search-input {
		display: flex;
		background-color: #f7f7f7;
		height: 73rpx;
		margin: 170rpx 30rpx 30rpx 30rpx;
		border-radius: 50rpx;
		align-items: center;
	}

	.index-search-input text:nth-child(1) {
		//	margin: 0rpx 27rpx;
		margin-left: 27rpx;
	}

	.index-search-input text:nth-child(2) {
		flex: 1;
		font-size: 30rpx;
		margin: 0 27rpx;
		color: #959FA0
	}

	.index-list {
		margin: 0 30rpx;
	}

	.index-list-item {
		display: flex;
		margin-bottom: 35rpx;

	}

	.index-list-item-img {
		height: 212rpx;
		width: 212rpx;
		margin-right: 20rpx;
		border-radius: 15rpx;
		overflow: hidden;
		position: relative;
	}

	.index-list-item-img image {
		width: 100%;
		height: 100%;
	}

	.index-list-item-img text {
		position: absolute;
		font-size: 22rpx;
		color: white;
		bottom: 15rpx;
		left: 15rpx;
	}

	.index-list-item-text {
		flex: 1;
		font-size: 24rpx;
		line-height: 68rpx;
	}

	//轮播图样式
	.banners {
		line-height: 40rpx;
	}

	.banner-swiper-item {
		display: flex;
		justify-content: center;
		height: 100%;
		align-items: center;
	}

	.banner-swiper image {
		width: 100%;
		margin: 0 30rpx;
		border-radius: 20rpx;
		justify-content: center;
		align-items: center;
	}

	/* 	.banner-swiper view{
		display: flex;
		position: relative;
	} */

	//歌手样式
	.artists {
		display: flex;
		margin: 30rpx;
		flex-direction: column;
	}

	.column-top {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 15rpx;
	}

	.icon-more {
		float: right;
		margin-right: 20rpx;

	}

	.artist-list,
	.rank {
		display: flex;
		width: 100%;
		white-space: nowrap;
	}

	.artist-list-item {
		display: inline-block;
		margin-right: 20rpx;
		justify-content: center;
		align-items: center;
		text-align: center;
		font-size: 32rpx;
	}

	.artist-list-item image {
		height: 180rpx;
		border-radius: 15rpx;
	}

	//排行榜
	.rankList {
		display: flex;
		margin: 30rpx;
		flex-direction: column;
	}

	.rank-item {
		display: inline-block;
		margin: 5rpx 15rpx;
		width: 636rpx;
		height: 530rpx; //530+200
		margin-bottom: 200rpx;
		box-shadow: 1rpx 1rpx 3rpx 3rpx #979797;
		border-radius: 15rpx;

	}

	.rank-item-name {
		font-size: 34rpx;
		font-weight: bold;
		text-align: center;
		margin: 15rpx;

	}

	.rank-item-content {
		margin: 10rpx 20rpx;
		height: 80rpx;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		line-height: 80rpx;
		position: relative;
		width: 90%;
	}

	.rank-item-content image {
		width: 72rpx;
		height: 72rpx;
		border-radius: 15rpx;
		/* display: inline-block; */
	}

	/* 	.rank-item-content-song{
		flex-direction: column;
	} */
	.rank-item-content view {
		display: inline-block;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		
	}

	.rank-item-content view:nth-child(2) {
		font-weight: bold;
		margin: 0 10rpx;
		font-size: 28rpx;
	}

	.rank-item-content view:nth-child(3) {
		font-size: 28rpx;
		max-width: 55%;
	}

	.rank-item-content view:nth-child(4) {
		font-size: 26rpx;
		color: gray;
		max-width: 20%;
	}

	.rank-item-content text {
		right: 5rpx;
		position: absolute;

	}

	/* 
	swiper {
		width: 100%;
		 height: calc(100vw * 327 /  491); 
	} */


	/* image {
	  width: 100%;
	} */


	/*	.logo {
		height: 200rpx;
		width: 200rpx;
		margin-top: 200rpx;
		margin-left: auto;
		margin-right: auto;
		margin-bottom: 50rpx;
	}

	.text-area {
		display: flex;
		justify-content: center;
	}

	.title {
		font-size: 36rpx;
		color: #8f8f94;
	} */
</style>
