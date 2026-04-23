<template>
	<view class="playlists">
		<musichead title="歌单排行榜" icon="true"></musichead>
		<view class="container">
			<scroll-view class="list" scroll-y="true">
				<view class="list-item" v-for="(item,index) in playlists" :key="item.id"
					@tap="handleToList(item.id)">
					<view class="list-item-img">
						<image :src="item.coverimgurl" mode="heightFix"></image>
					</view>
					<view class="list-item-name">
						{{item.name}}
					</view>
					
				</view>
			</scroll-view>
		</view>
		<footermusic bottom="0rpx"></footermusic>
	</view>
</template>

<script>
	import {
		getTotalPlaylist
	} from '../../common/api.js'
		import '../../static/iconfont/iconfont.css'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import musichead from '../../components/musichead/musichead.vue'
	export default {
		data() {
			return {
				playlists: {},

			}
		},
		components:{
			musichead,
			footermusic
		},
		onShow() {

		},
		onLoad() {
			getTotalPlaylist().then(res => {
				if (res != null) {
					this.playlists = res;
				}
			})
		},
		methods: {
			handleToList(id) {
				console.log(id)
				uni.navigateTo({
					url: '/pages/list/list?id=' + id,
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
