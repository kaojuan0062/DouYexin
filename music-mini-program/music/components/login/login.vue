<!-- "https://thirdwx.qlogo.cn/mmopen/vi_32/POgEwh4mIHO4nibH0KlMECNjjGxQUq24ZEaGT4poC6icRiccVGKSyXwibcPq4BWmiaIGuG1icwxaQX6grC9VemZoJ8rg/132" -->
<template>
	<view class="login" v-if="loginShow" :class="{show:loginShow}">
		<view @tap="closeLogin" class="mask" bind:tap="cancel" catch:touchmove="emptyHandler"></view>
		<view class="container">
		<!-- 	<view v-if="getUserInfoTag"> -->
				<view class="close-box" @tap="closeLogin" bind:tap="cancel">
					<text class="iconfont icon-cancel"></text>
				</view>

				<view class="title">
					你好
				</view>
<!-- 				<button class="submit-btn" open-type="getUserInfo" @tap="getUserInfo">
					<text class="iconfont icon-wechat"></text>
					<text class="wechat-text">微信一键登录</text>
				</button> -->
				<view  class="submit-btn" @tap="getUserInfo">
					<text class="iconfont icon-wechat"></text>
					<text class="wechat-text">微信一键登录</text>
				</view>
				<view class="serve-info">点击登录/注册，即表示已阅读并同意</view>
				<view class="serve-text">
					<view @tap="gotoWeb('https://uniapp.dc.dcloud.io/component/mp-weixin-plugin')">隐私协议</view>
					<view @tap="gotoWeb('https://developers.weixin.qq.com/miniprogram/dec/framework/')">用户协议</view>
				</view>
<!-- 			</view> -->

		</view>
		<!-- 获取手机号 -->
		<!-- 		<view class="getMobile" v-if="getUserMobileTag">
			<view class="">
				一键获取手机号，完成登录/注册
			</view>
			<button class="submit-btn" open-type="getPhoneNumber" @tap="getUserMobile" >
				<text class="iconfont icon-wechat"></text>
				<text class="wechat-text">获取手机号</text>
			</button>
		</view> -->

	</view>
</template>

<script>
	// import personInfo from '../personInfo/personInfo.vue'
	import {thisUrl}from '../../common/config.js'
	import {
		mapMutations
	} from 'vuex'
	import {
		getOpenid,
		isExist,
		register,
		getUser,updateUser
	} from '../../common/api.js'
	export default {
		name: "login",
		props: ['loginShow'],
		data() {
			return {
				show: true,
				getUserInfoTag: true,
				//fillInfoTag: false,
				userInfo: {
					id:'',
					openid: '',
					sessionkey: '',
					nickName: '',
					mobile: '',
					createtime: '',
					userpic: ''
				},
			}
		},
		methods: {
			...mapMutations(['updateUserInfo', 'saveUserInfoToStorge', 'updateCheckSession', 'saveCheckSessionToStorge']),
			closeLogin() {
				this.$emit("changeloginShow",false);
				//this.show = false;
			},
			// openLogin() {
			// 	this.show = true;
			// },
			getUserInfo() {
				console.log("注册！！！")
				uni.getUserProfile({
					//lang: 'zh_CN',
					desc: "仅用作登录功能",
					success: res => { //授权成功
						console.log("uni.getUserProfile==", res)
						this.userInfo.nickName = res.userInfo.nickName;
						this.userInfo.userpic = res.userInfo.avatarUrl;
						this.updateUserInfo(this.userInfo);
						uni.login({
							
							provider: 'weixin',
							success: lres => { //登录成功
								console.log("uni.login==" + JSON.stringify(lres))
								var code = lres.code;
								getOpenid(code).then(openres => {
									var data = openres[1].data;
									this.userInfo.openid = data.openid;
									this.userInfo.sessionkey = data.session_key;
									//判断是否存在
									isExist(data.openid).then(user => {
										if (user == false) { //不存在，注册
											register(this.userInfo).then(reg => {
												if (reg.openid != null) {
													this.userInfo.id=reg.id;
													this.updateUserInfo(this.userInfo);
													this.updateCheckSession(true)
													this.closeLogin();
												} else {
													uni.showModal({
														title: '提示',
														content: '注册失败',
														success: function(res) {
															if (res.confirm) {console.log('用户点击确定');} 
															else if (res.cancel) {console.log('用户点击取消');}
														}
													})
												}
											});
										} else { //已注册
											getUser(this.userInfo.openid).then(getuser=>{
												if(getuser!=null){
													this.userInfo=getuser
													this.updateUserInfo(this.userInfo);
													this.updateCheckSession(true)
													this.closeLogin();
												}
											})											
										}
									})
								})
							},
							fail: (err) => {
								console.log("登录失败" + err)
							//	this.$emit("changeloginShow",false);
							}
						})
					},
					fail: (err) => {
						console.log("用户取消授权" + JSON.stringify(err))
					}
				})
			},
			gotoWeb(url) {
				uni.navigateTo({
					url: url
				})
			},
		}
	}
</script>

<style lang="scss" scoped>
	.login {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		left: 0;
		display: flex;
		align-items: flex-end;
		opacity: 1;
		transition: opacity 300, z-index 0 300;
		pointer-events: none;
		z-index: 9999;

		&.show {
			position: fixed;
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

			.title {
				margin-top: 48rpx;
				font-size: 36rpx;
				font-weight: normal;
			}

			.close-box {
				position: absolute;
				right: 32rpx;
				top: 38rpx;
				width: 56rpx;
				height: 56rpx;
				padding: 10rpx;

				.icon-cancel {

					width: 56rpx;
					height: 56rpx;

				}
			}
		}

		.submit-btn {
			width: 642rpx;
			height: 80rpx;
			margin-top: 60rpx;
			margin-bottom: 60rpx;
			border-radius: 44rpx;
			display: flex;
			flex-direction: row;
			align-items: center;
			justify-content: center;
			color: white;
			background-color: #658257;
			font-size: 36rpx;

			.icon-wechat {
				font-size: 40rpx;

			}

			.wechat-text {
				margin-left: 20rpx;
				height: 44rpx;
				line-height: 44rpx;
				color: white;
				font-size: 35rpx;
			}

		}

		.serve-info {
			font-size: 22rpx;
			margin-top: 20rpx;
		}

		.serve-text {
			display: flex;
			flex-direction: row;
			align-items: center;
			justify-content: center;
			font-size: 22rpx;
			margin-top: 10rpx;
			color: #6079b8;

			view:nth-child(1) {
				margin-right: 15rpx;
			}
		}




	}

	button::after {
		border: none;
	}
</style>
