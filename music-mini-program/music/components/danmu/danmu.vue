<template>
	<view class="danmu" :class="{show:dmShow}">
		<view class="dmGroup top ">
			<view class="dmItem" v-for="(item,index) in danmulist" :key="item.id">
				<view class="dm " :class="item.sendTime>=(currentTime-3)&&item.sendTime<=(currentTime+1)?'moving':''">
					<image class="dm-pic" :src="item.userPic" mode="aspectFit"></image>
					<text class="dm-content">{{item.content}}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		getDanmus
	} from '../../common/api.js'
	import {
		mapState,
		mapMutations
	} from 'vuex'
	export default {
		name: "danmu",
		props: ['dmShow'],
		data() {
			return {
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
				preTime: '',
				nextTime: '',
				animationData: {}

			}
		},
		computed: {
			...mapState(['thisSong', 'currentTime']),
		},
		mounted() {
			//this.setCurrentTime(this.currentTime)
			//this.preTime=this.currentTime+1
			this.setThisSong(this.thisSong)
			getDanmus(this.thisSong.id).then(res => {
				if (res != null) {
					this.danmulist = res;
					console.log("弹幕组件" + JSON.stringify(this.danmulist))
				}
			})
			console.log("弹幕组件")
			this.animation = uni.createAnimation();
		},
		methods: {
			...mapMutations(['setIsPlaying', 'setThisSong', 'setSonglist', 'setCurrentTime', 'setDuration', 'setIds',
				'setMusicUrl', 'setIsChanging', 'setTimeStr'
			]),
			getDanmusAgain(songid) {
				getDanmus(songid).then(res => {
					if (res != null) {
						this.danmulist = res;
						//console.log("发送弹幕成功后刷新" + JSON.stringify(this.danmulist))
					}
				})
			}
			// running() {
			// 	this.animation.translateX(500).step({
			// 		duration: 1000
			// 	})
			// 	// 调用实例的方法来描述动画,translateX定义动画类型为x轴偏移, 500为偏移长度, 单位px
			// 	// 调用 step() 来表示一组动画完成(当前参数动画时间1s)
			// 	// step 可以配置参数用于指定当前组动画的配置。具体参数请看文档
			// 	this.animationData = this.animation.export()
			// }

		}

	}
</script>

<style lang="scss">
	.moving {
		position: fixed;
		z-index: 20;
		-webkit-animation: mymove 40s 1 linear;
		animation: mymove;
		animation-duration: 25s;
		animation-timing-function: linear;
		animation-iteration-count: 1;
		animation-fill-mode: none;
		transform: translateZ(0);
		white-space: nowrap;
	}

	.danmu {
		width: 100%;
	}

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
		top: 250rpx;
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

	// 动画
	@keyframes mymove {
		from {
			left: 0%;
		}
		to {
			left: 800%;
		}
	}

	@-moz-keyframes mymove

	/* Firefox */
		{
		from {
			left: 0%;
			//left: 0px;
		}

		to {
			left: 1000%;
		}
	}

	@-webkit-keyframes mymove

	/* Safari and Chrome */
		{
		from {
			left: 0%;
			//left: 0px;
		}

		to {
			left: 1000%;
		}
	}
</style>
