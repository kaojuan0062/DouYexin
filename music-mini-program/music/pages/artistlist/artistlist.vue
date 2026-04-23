<template>
	<view class="artistlist">
		<musichead title="热门歌手" icon="true"></musichead>
		<view class="container">
			<scroll-view class="list" scroll-y="true">
				<view class="list-item" v-for="(item,index) in artistlist" :key="item.id"
					@tap="handleToArtist(item.id)">
					<view class="list-item-img">
						<image :src="item.picurl" mode="heightFix"></image>
					</view>
					<view class="list-item-name">
						{{item.name}}
					</view>
					<!-- 				<view class="list-item-text">
					<view v-for="(musicItem,index) in item.tracks" :key="index">
						{{index+1}}.{{musicItem.first}}-{{musicItem.second}}
					</view>
				</view> -->
				</view>
			</scroll-view>
		</view>
		<footermusic bottom="0rpx"></footermusic>
	</view>
</template>

<script>
	import {
		getArtists
	} from '../../common/api.js'
		import '../../static/iconfont/iconfont.css'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import musichead from '../../components/musichead/musichead.vue'
	export default {
		data() {
			return {
				artistlist: {},

			}
		},
		components:{
			musichead,
			footermusic
		},
		onShow() {

		},
		onLoad() {
			getArtists().then(res => {
				if (res != null) {
					this.artistlist = res;
				}
			})
		},
		methods: {
			handleToArtist(id) {
				console.log(id)
				uni.navigateTo({
					url: '/pages/artist/artist?id=' + id,
				});
			},
		}
	}
</script>

<style lang="scss" scoped>
	.container{
		height: 78vh;
	}
	.list{
		margin: 30rpx;
		margin-bottom: 130rpx;
		height: 95%;
	}
	.list-item {
		display: flex;
		margin-bottom: 35rpx;

	}

	.list-item-img {
		height: 150rpx;
		//width: 180rpx;
		margin-right: 20rpx;
		border-radius: 15rpx;
		overflow: hidden;
		position: relative;
	}

	.list-item-img image {
		width: 100%;
		height: 100%;
	}
	.list-item-name{
		font-weight: bold;
		font-size: 36rpx;
		margin-top:50rpx;
	}
</style>
