<template>
	<view class="tabbar">
		<view class="tabbar-list">
			<view class="tabbar-list-ul">
				<view v-for="(item,index) in tabBar.list" :key="index"
					:class="selected==index?'tabbar-list-li active':'tabbar-list-li'" @click="setSelected(index)">
					<view class="tabbar-list-li-icon">
						<text :class="selected==index?item.selectedIconPath:item.iconPath"></text>
					</view>
					<view class="tabbar-list-li-name">
						{{item.text}}
					</view>
				</view>
			</view>
		</view>
		<login ref="login" :loginShow="loginShow" @changeloginShow="changeloginShow"></login>
		<!-- <login ref="login" v-if="loginShow"></login> -->
	</view>
</template>

<script>
	import {
		mapState
	} from 'vuex'
	export default {
		name: "tabbar",
		props: ['selected'],
		data() {
			return {
				loginShow: false,
				tabBar: {
					list: [{
							pagePath: '/pages/index/index',
							iconPath: "iconfont icon-faxian",
							selectedIconPath: "iconfont icon-faxianed",
							text: "发现",
						},
						{
							pagePath: '/pages/person/person',
							iconPath: "iconfont icon-person",
							selectedIconPath: "iconfont icon-personed",
							text: "我的",
						}
					]
				},
			};
		},
		created() {

		},
		computed: {
			...mapState(['checkSession'])
		},
		methods: {
			setSelected(index) {
				console.log("转换到", index)
				//判断是否登录
				if (index == 1) {
					if (this.$store.state.checkSession==true) {
						console.log("转换到1检查session为true")
						this.loginShow = false;
						uni.switchTab({
							url: this.tabBar.list[index].pagePath
						})
					} else {
						console.log("转换到1检查session为false")
						this.loginShow = true;
					}
				} else {

					uni.switchTab({
						url: this.tabBar.list[index].pagePath
					})
					this.loginShow = false;
				}
			},
			changeloginShow(isShow) { //组件传值
				this.loginShow= isShow
			},
		}
	}
</script>

<style lang="scss" scoped>
	.tabbar {
		width: 100%;
		position: fixed;
		box-sizing: border-box;
		z-index: 99;
	}

	.tabbar-list {
		width: 100%;
		color: #344356;
		background: #ffffff;
		position: fixed;
		left: 0;
		bottom: 0;
	}

	.tabbar-list-ul {
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: space-around;
		align-items: center;
		box-sizing: border-box;
	}

	.tabbar-list-li-icon {
		width: 56rpx;
		height: 56rpx;
		margin: 0 auto;
		padding: 20rpx 0;
	}

	.tabbar-list-li-icon text {
		font-size: 56rpx;
	}

	.tabbar-list-li-name {
		width: 100%;
		text-align: center;
		line-height: 40rpx;
		font-size: 20rpx;
		height: 40rpx;
		font-family: Microsoft YaHei;
	}

	.active {
		color: #658257;
	}
</style>
