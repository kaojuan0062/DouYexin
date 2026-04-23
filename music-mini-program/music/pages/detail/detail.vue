<template>
	<view class="detail">
		<view class="fixbg" style="backgroundImage:'url(../../static/ogo.png)'"></view>
		<musichead title="歌单" :icon="true" color="white"></musichead>
		<view class="container">
			<view class="detail-play">
				<image src="../../static/wyyLogo.png"></image>
				<text class="iconfont icon-zanting"></text>
				<view class="">
					
				</view>
			</view>
		</view>
		
	</view>
</template>

<script>
	import '../../static/iconfont/iconfont.css'
	import musichead from '../../components/musichead/musichead.vue'
	export default {
		
		data() {
			return {
				icon:true,
				
			}
		},
		onLoad(options) {
			//console.log(options.songId);
			
		},
		methods: {
			
			
		}
	}
</script>

<style>
	.detail{
		overflow: hidden;
	}
	.detail-play{
		width: 580rpx;
		height: 580rpx;
		background-image: url(../../static/disc.png);
		background-size: cover;
		margin: 210rpx auto 44rpx auto;
		position: relative;
	}
	.detail-play image{
		width:380rpx;
		height: 380rpx;
		border-radius: 50%;
		position: absolute;
		left: 0;
		top: 0;
		right: 0;
		bottom: 0;
		margin: auto;
		animation: 10s linear infinite discRotation;
		animation-play-state: paused;
	}
	.detail-play text{
		width:100rpx;
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
	.detail-play view{
		position: absolute;
		width: 170rpx;
		height: 266rpx;
		left: 90rpx;
		right: 0;
		top: -170rpx;
		margin: auto;
		background: url(../../static/needle.png);
		background-size: cover;
	}
	
	@keyframes discRotation{
		from{
			transform: rotate(0);
		}
		to{
			transform: rotate(360);
		}
	}

</style>
