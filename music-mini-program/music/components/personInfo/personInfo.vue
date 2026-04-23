<template>
	<view id="personInfo" class="personInfo" :class="{show:show}">
		<view @tap="closeInfo()" class="mask" bind:tap="cancel" catch:touchmove="emptyHandler"></view>
		<view class="container">

			<view class="title">
				{{title}}
			</view>
			<view class="close-box" @tap="closeInfo()" bind:tap="cancel">
				<text class="iconfont icon-cancel"></text>
			</view>
			<view class="info-content">
				<view class="info-item info-pic-item">
					<view class="info-item-name">头像</view>
					<button open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
						<!-- 	<image @tap="changeUserPic"  :src="userinfo.userpic"></image> -->
						<image :src="userinfo.userpic"></image>
					</button>
					<!-- 	</view> -->
					<text class="iconfont icon-right"></text>
				</view>
				<view class="info-item">
					<view class="info-item-name">昵称</view>
					<!-- <view class="info-item-text">
						考卷
						<text class="iconfont icon-right"></text>
					</view> -->
					<input type="nickname" v-model="userinfo.nickName" name="nickName" />
					<text class="iconfont icon-right"></text>
				</view>
				<view class="info-item">
					<view class="info-item-name">手机号</view>
					<!-- 					<view class="info-item-text">
						19888888
						<input type="nickname" />
						<text class="iconfont icon-right"></text>
						
					</view> -->
					<input type="number" v-model="userinfo.mobile" name="mobile" />
					<text class="iconfont icon-right"></text>
				</view>
			</view>
			<button class="submit-btn" @tap="updatePersonInfo">
				<text class="wechat-text">完成</text>
			</button>
		</view>
	</view>
</template>

<script>
	import {
		thisUrl
	} from '../../common/config.js'
	import {
		getUser,
		updateUser
	} from '../../common/api.js'
	import {
		mapMutations
	} from 'vuex'
	export default {
		name: "personInfo",
		el: "#personInfo",
		props: ['title'],
		data() {
			return {
				show: true,
				userinfo: {
					id: '',
					openid: '',
					sessionkey: '',
					nickName: '',
					mobile: '',
					createtime: '',
					userpic: ''
				}
			};
		},
		created() {

			this.userinfo = JSON.parse(this.$store.state.userinfo)
			// console.log("personInfo从store中获取的userinfo=="+JSON.stringify(this.userinfo))
			console.log("personInfo从store中获取的userinfo==" + this.userinfo.nickName)
		},
		methods: {
			...mapMutations(['updateUserInfo', 'saveUserInfoToStorge', 'updateCheckSession', 'saveCheckSessionToStorge']),
			closeInfo() {
				show = false
			},
			//修改用户信息
			updatePersonInfo() {
				if (this.userinfo.mobile == null || this.userinfo.mobile == "" || this.userinfo.mobile == undefined) {
					uni.showModal({
						title: '提示',
						content: '请输入手机号',

					})
					return
				}
				if (this.userinfo.nickName == null || this.userinfo.nickName == "" || this.userinfo.nickName ==
					undefined) {
					uni.showModal({
						title: '提示',
						content: '请输入昵称',
					})
					return
				}
				if (this.userinfo.userpic == null || this.userinfo.userpic == "" || this.userinfo.userpic == undefined) {
					uni.showModal({
						title: '提示',
						content: '请上传头像',
					})
					return
				}
				var user = getUser(this.userinfo.openid);
				user.nickName = this.userinfo.nickName;
				user.userpic = this.userinfo.userpic;
				user.mobile = this.userinfo.mobile;
				this.userinfo = updateUser(user);
				if (this.userinfo != null) {
					this.updateUserInfo(this.userinfo);
					this.closeInfo();
				}
			},
			//获取微信头像
			onChooseAvatar(e) {
				console.log("获取微信头像"+e.detail);
			},
			//修改头像
			changeUserPic() {
				let that = this;
				uni.chooseImage({
					count: 1,
					sizeType: ["original", "compressed"], //可以指定是原图还是压缩图，默认二者都有
					sourceType: ["album", "camera"], //从相册选择或者打开相机
					success: function(res) {
						if (res.tempFiles[0].size > 2 * 1024 * 1024) {
							_this.$refs.uToast.show({
								type: "error",
								message: "图片大小不得超过2MB"
							});
						} else {
							uni.uploadFile({
								url: `${thisUrl}FileUploads`,
								filePath: res.tempFilePaths[0],
								name: "file",
								success: uploadFileRes => {
									// 根据返回的uploadFileRes.data做操作，往下逻辑要怎么写关键还是要看后端如何处理。就当前逻辑该上传接口返回的是图片需要的一个ID
									// 该方法是通过将uploadFileRes.data中的667值传参给后端，后端返回ArrayBuffer对象，最后在专程Base64字符串
									//_this.showPhoto(uploadFileRes.data)
									console.log("上传图片=" + uploadFileRes.data)
									that.userinfo.userpic = uploadFileRes.data
								}

							});
						}
					}
				})

			},


			// 转base64,将ArrayBuffer对象，转成Base64字符串，最后赋值
			// showPhoto(data) {
			// 	this.$http
			// 		.showPhoto({
			// 			id: JSON.parse(data.data.id),
			// 			size: "300"
			// 		})
			// 		.then(res => {
			// 			const arrayBuffer = new Uint8Array(res.data);
			// 			this.userPhoto = `data:image/jpeg;base64,${uni.arrayBufferToBase64(arrayBuffer)}`;

			// 		});
			// }

		}
	}
</script>

<style lang="scss" scoped>
	.personInfo {
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

		.info-content {
			padding: 10rpx 30rpx;
			width: 100%;
		}

		.info-item {
			width: 100%;
			height: 100rpx;
			line-height: 100rpx;
			border-top: 1px solid #808080;
			margin: 5rpx 0;
			flex-flow: row;

			//display: block;
			display: flex;
			flex: 1;

			// justify-content: center;
			input {
				width: 50%;
				text-align: right;
				position: fixed;
				right: 10%;
				height: 60rpx;
				margin-top: 20rpx;
				background-color: red;
				color: #808080;
			}

			text {
				position: fixed;
				right: 5%;
			}

			image {
				position: fixed;
				right: 10%;
				margin-top: 10rpx;
				width: 100rpx;
				height: 100rpx;
			}

		}

		.info-item-name {
			margin-left: 20rpx;
		}

		// .info-item-text {
		// 	margin-right: 20rpx;
		// 	color: #808080;
		// }


		.info-pic-item {
			height: 120rpx;
			line-height: 120rpx;

			// .info-item-text {
			// 	// text {
			// 	// 	position: fixed;
			// 	// 	text-align: center;
			// 	// 	right: 35rpx;
			// 	// }

			// 	image {
			// 		margin-top: 10rpx;
			// 		width: 100rpx;
			// 		height: 100rpx;
			// 		// position: around;
			// 		// right: 20rpx;
			// 		// top: 10rpx;
			// 	}
			// }
		}

		.submit-btn {
			width: 642rpx;
			height: 80rpx;
			margin: 30rpx auto;
			border-radius: 44rpx;
			align-items: center;
			justify-content: center;
			color: white;
			background-color: #658257;
			font-size: 36rpx;
			line-height: 80rpx;
		}

	}
</style>
