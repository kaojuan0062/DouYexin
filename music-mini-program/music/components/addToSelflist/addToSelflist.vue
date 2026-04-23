<template>
	<view class="add-to-selflist" v-if="atslShow" :class="{show:atslShow}">
		<view @tap="closeWindow()" class="mask" bind:tap="cancel" catch:touchmove="emptyHandler"></view>
		<view class="container ">

			<view class="title">
				收藏到歌单
			</view>
			<view class="close-box" @tap="closeWindow()" bind:tap="cancel">
				<text class="iconfont icon-cancel"></text>
			</view>
			<view class="selflist-box">
				<scroll-view scroll-y="true">
					<view class="selflist-item" v-for="(item,index) in selflists" :key="index" @tap="addSongtoSelflist(item.id)">
						<view class="selflist-item-img">
							<image mode="aspectFill" :src="item.coverPic"></image>
						</view>
						<view class="selflist-item-text">
							<view>{{item.name}}</view>
							<view>{{item.songSize}}首</view>
						</view>
					</view>
				</scroll-view>
			</view>
			<!-- 			<button class="submit-btn" @tap="addSongtoSelflist()">
				<text class="btn-text">完成</text>
			</button> -->
		</view>
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import {
		getSelflistsOfUser,
		addSongToSelflist
	} from '../../common/api.js'
	export default {
		name: "addToSelflist",
		props: ['atslShow','songid'],
		data() {
			return {
				userinfo:{},
				selflists: [{}], //自建歌单列表
			};
		},
		mounted() {
			this.userinfo = this.$store.state.userinfo
			if (typeof this.userinfo === 'string') {
				this.userinfo = JSON.parse(this.$store.state.userinfo)
			}
			//获取用户自建歌单
			getSelflistsOfUser(this.userinfo.openid).then(res => {
				if (res != null) {
					this.selflists = res;
					console.log("获取自建歌单"+this.selflists)
				}
			})
		},
		methods: {
			closeWindow() {
				this.$emit("changeShowAddtoSl", false);
			},
			addSongtoSelflist(listid) {
				addSongToSelflist(this.songid,listid,this.userinfo.openid).then(res=>{
					if(res===null||res===""){
						uni.showModal({
							title: '提示',
							content: '该歌曲已存在此歌单中',
						})
						return;
					}
					this.selflists=res
					uni.showToast({
						title: '歌曲添加成功',
						icon: 'success',//图标
					    mask: true,//是否显示透明蒙层，防止触摸穿透，默认：false
					});
					this.closeWindow();
				});
			}
		}
	}
</script>

<style lang="scss" scoped>
	.add-to-selflist {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		left: 0;
		display: flex;
		align-items: flex-end;
		opacity: 0;
		transition: opacity 300, z-index 0 300;
		pointer-events: none;
		z-index: 999;

		&.show {
			z-index: 9999;
			opacity: 1;
			pointer-events: auto;
		}

		.mask {
			position: fixed;
			width: 100%;
			height: 100%;
			background-color: rgba($color: #000000, $alpha: 0.3);
		}

		.container {
			z-index: 999;
			display: flex;
			flex-direction: column;
			width: 100%;
			padding: 40rpx 20rpx;
			background-color: #f1f1f1;
			border-radius: 20rpx;
			align-items: center;
			position: relative;
		}

		.close-box {
			position: absolute;
			right: 32rpx;
			top: 38rpx;
			width: 56rpx;
			height: 56rpx;
			padding: 10rpx;
		}

		.icon-cancel {

			width: 56rpx;
			height: 56rpx;
		}

		.title {
			font-weight: bold;
			font-size: 36rpx;
			height: 100rpx;
			line-height: 100rpx;
		}
		.selflist-item-img {
			height: 84rpx;
			width: 84rpx;
			margin-left: 24rpx;
			margin-top: 18rpx;
			border-radius: 15rpx;
			text-align: center;
			justify-content: center;
			overflow: hidden;
		
		
		}
		
		.selflist-item-img image {
			width: 100%;
			height: 100%;
		}
		
		.selflist-item-text {
			/* position: absolute;
			left: 134rpx;
			top: 13px; */
			margin-left: 140rpx;
			margin-top: -82rpx;
		}
		
		.selflist-item-text view:nth-child(1) {
			height: 40rpx;
			line-height: 40rpx;
			font-size: 32rpx;
		}
		
		.selflist-item-text view:nth-child(2) {
			color: #808080;
			font-size: 24rpx;
		}
		
		.selflist-box {
			display: flex;
			width: 100%;
			height: 400rpx;
			padding: 0 5% 5% 5%;
		}
		
	}
</style>
