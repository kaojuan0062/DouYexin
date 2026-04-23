<template>
	<view class="search">
		<musichead title="搜索" icon="true"></musichead>
		<view class="container">
			<view class="search-top">
				<view class="search-input">
					<text class="iconfont icon-search"></text>
					<input type="text" placeholder="搜索歌曲" auto-focus="true" v-model="searchKey" name="searchKey"/>
				</view> 
				<button class="search-btn" @tap="searchSongs">搜索</button>
			<!-- 	<uni-search-bar placeholder="搜索歌曲"></uni-search-bar> -->
			</view>
			<view class="nullContent" v-if="isSearched&&!isExist">暂无此内容</view>
			<scroll-view v-if="isSearched&&isExist" scroll-y="true" class="search-content">
				<view class="search-item" v-for="(item,index) in searchList" :key="item.id" @tap="handleToDetail(item)">
					<image :src="item.picurl"></image>
					<view class="songname">{{item.name}}</view>
					<view class="artistname">-{{item.artistName}}</view>
					<text class="iconfont icon-playCircle"></text>
				</view>
			</scroll-view>
		</view>
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	import {
		mapState,
		mapMutations,
		mapActions
	} from 'vuex'
	import {
		searchSongs	
	} from '../../common/api.js'
	export default {
		data() {
			return {
				searchList: [{}],
				searchKey:'',
				isExist:false,
				isSearched:false
				
			}
		},
		components: {
			musichead
		},
		onLoad() {
			this.searchList=[]
			this.searchKey=''
			this.isExist="false"
			this.isSearched="false"
		},
		methods: {
			...mapMutations(['setSonglist', 'setIds'
			]),
			searchSongs(){
				this.isSearched=true;
				searchSongs(this.searchKey).then(res=>{
					if(res!=null){
						this.searchList=res
						console.log("搜索到的歌曲"+this.searchList)
						//若无搜索内容则显示“暂无内容”
						if(this.searchList!=""&&this.searchList!=null){
							this.isExist=true
						}else{
							this.isExist=false
						}
					}
				})
			},
			handleToDetail(song) {
				let songIds = []
				let songlist = []
				songlist.push(song)
				this.setSonglist(songlist);
				songIds.push(song.id)
				this.setIds(songIds)
				uni.navigateTo({
					url: '/pages/play/play?songId=' + song.id +
						'&ids=' + songIds,
				})
			},
		}
	}
</script>

<style lang="scss" scoped>
	.search-top {
		display: flex;
		height: 75rpx;
		margin: 30rpx 30rpx 30rpx 30rpx;
		justify-content: space-between;
	}

	.search-input {
		display: flex;
		background-color: #f7f7f7;
		height: 73rpx;
		border-radius: 50rpx;
		align-items: center;
		width: 75%;
	}

	.search-input text:nth-child(1) {
		//	margin: 0rpx 27rpx;
		margin-left: 27rpx;
	}

	.search-input text:nth-child(2) {
		flex: 1;
		font-size: 30rpx;
		margin: 0 27rpx;
		color: #959FA0
	}
	.search-btn{
		background-color: #658257;
		color: white;
		height: 70rpx;
		line-height: 70rpx;
		font-size: 30rpx;
		border-radius: 50rpx;
		width: 20%;
		
	}
	//搜索结果
	.search-content{
		margin: 0rpx 30rpx 30rpx 30rpx;
		width: 100vh;
		height: 80%rpx;
	}
	.search-item{
		display: flex;
		width: 100%;
		height: 120rpx;	
		white-space: nowrap;
		text-overflow: ellipsis;
		line-height: 120rpx;
		justify-items: center;
		image{
			width:100rpx;
			height: 100rpx;
			border-radius: 15rpx;
		}
		.songname{
			height: 120rpx;
			line-height: 120rpx;
			margin-left: 30rpx;
			
		}
		.artistname{
			height: 120rpx;
			line-height: 120rpx;
			font-size: 30rpx;
			color: #959FA0;
		}
		text{
			position: fixed;
			right: 30rpx;
		}
		
	}
	.nullContent{
		width: 100%;
		font-size: 36rpx;
		color: #959FA0;
		margin: auto;
		justify-content: center;
		text-align: center;
	}
	
</style>
