<template>
	<view class="createSelflist" v-if="createShow" :class="{show:createShow}">
		<view @tap="closeWindow()" class="mask" bind:tap="cancel" catch:touchmove="emptyHandler"></view>
		<view class="container ">
			<view class="title">
				{{title}}
			</view>
			<view class="close-box" @tap="closeWindow()" bind:tap="cancel">
				<text class="iconfont icon-cancel"></text>
			</view>
			<view class="cl-content cl-add" v-if="title==='新建歌单'">
				<view class="cl-item">
					<view class="cl-item-name">歌单名称</view>
					<input type="text" v-model="addselflist.name" name="name" placeholder="请输入歌单名称" />
					<text class="iconfont icon-right"></text>
				</view>
				<view class="cl-item cl-pic-item">
					<view class="cl-item-name">封面</view>
					<button class="choose-image" @tap="chooseCoverpic">
						<image mode="aspectFill" :src="addselflist.coverPic" v-if="addselflist.coverPic!=null"></image>
					</button>
					<text class="iconfont icon-right"></text>
				</view>
				<view class="cl-item cl-item-desc">
					<view class="cl-item-name">简介</view>
					<textarea v-model="addselflist.description" name="description" rows="5"></textarea>
					<text class="iconfont icon-right"></text>
				</view>
			</view>
			<view class="cl-content cl-update" v-if="title==='编辑歌单'">
				<view class="cl-item">
					<view class="cl-item-name">歌单名称</view>
					<input type="text" v-model="selflist.name" name="name" placeholder="请输入歌单名称" />
					<text class="iconfont icon-right"></text>
				</view>
				<view class="cl-item cl-pic-item">
					<view class="cl-item-name">封面</view>

					<button class="choose-image" @tap="chooseCoverpic">
						<!--  @tap="changeUserPic" -->
						<image mode="aspectFill" :src="chooseCover||selflist.coverPic" v-if="selflist.coverPic!=null">
						</image>
					</button>
					<!-- 	</view> -->
					<text class="iconfont icon-right"></text>
				</view>

				<view class="cl-item cl-item-desc">
					<view class="cl-item-name">简介</view>
					<textarea v-model="selflist.description" name="description" rows="5"></textarea>
					<text class="iconfont icon-right"></text>
				</view>
			</view>
			<button class="submit-btn" @tap="createSelflist()">
				<text class="btn-text">完成</text>
			</button>
		</view>
	</view>
</template>

<script>
	import {
		mapState
	} from 'vuex'
	import {
		createSelflist,
		updateSelfList
	} from '../../common/api.js'
	import {
		thisUrl
	} from '../../common/config.js'
	export default {
		name: "createSelflist",
		props: ['createShow', 'title', 'selflist'],
		data() {
			return {
				addselflist: {
					id: '',
					name: '',
					coverPic: '',
					description: '',
					createUserOpenid: '',
					createDate: '',
					status:0
				},
				userinfo: {},
				chooseCover: '',
			}
		},
		mounted() {
			// console.log("编辑歌单",JSON.stringify(this.listinfo))
			// if(this.listinfo!=null&&this.listinfo!=""){
			// 	this.selflist=this.listinfo
			// 	console.log("编辑歌单",JSON.stringify(this.selflist))
			// }
		},
		methods: {
			closeWindow() {
				//清空
				this.addselflist.name = '';
				this.addselflist.coverPic = '';
				this.addselflist.description = '';
				this.chooseCover='';
				this.$emit("changeShowCreate", false);
			},
			// openWindow(){
			// 	this.createShow=true;
			// }
			createSelflist() {
				this.userinfo = this.$store.state.userinfo
				if (typeof this.userinfo === 'string') {
					this.userinfo = JSON.parse(this.$store.state.userinfo)
				} 
				console.log(this.userinfo)
				if (this.title === "新建歌单") {
					//歌单名不能为空
					if (this.addselflist.name == null || this.addselflist.name == "" || this.addselflist.name ==
						undefined) {
						uni.showModal({
							title: '提示',
							content: '请输入歌单名称',
						})
						return
					}
					this.addselflist.createUserOpenid = this.userinfo.openid //设置创建者openid
					createSelflist(this.addselflist).then(res => {
						let status = res.statusCode;
						if (res.statusCode === 200) {
							uni.showToast({
								title: "新建歌单成功",
								icon: "success",
								mask: true
							})
							this.closeWindow();
						}
					})
					
				} else if (this.title === "编辑歌单") {
					console.log("准备编辑歌单")
					if (this.selflist.name == null || this.selflist.name == "" || this.selflist.name == undefined) {
						uni.showModal({
							title: '提示',
							content: '请输入歌单名称',
						})
						return
					}
					updateSelfList(this.selflist).then(res => {
						if (res.statusCode === 200) {
							uni.showToast({
								title: "编辑歌单成功",
								icon: "success",
								mask: true
							})
							this.closeWindow();
						}
					})
				}

			},
			//上传封面
			chooseCoverpic() {
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
								url: `${thisUrl}api/oss/file/fileUpload`,
								filePath: res.tempFilePaths[0],
								name: "file",
								success: uploadFileRes => {
									// 根据返回的uploadFileRes.data做操作，往下逻辑要怎么写关键还是要看后端如何处理。就当前逻辑该上传接口返回的是图片需要的一个ID
									// 该方法是通过将uploadFileRes.data中的667值传参给后端，后端返回ArrayBuffer对象，最后在专程Base64字符串
									console.log("上传图片=" + uploadFileRes.data)
									if (that.title === "编辑歌单") {
										that.chooseCover = uploadFileRes.data
										that.selflist.coverPic = uploadFileRes.data
										//console.log("编辑歌单上传图片=" + that.selflist.coverPic )
									} else if (that.title === "新建歌单") {
										that.addselflist.coverPic = uploadFileRes.data
									}
								}

							});
						}
					}
				})

			},
		}
	}
</script>

<style scoped lang="scss">
	.createSelflist {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		left: 0;
		display: flex;
		align-items: flex-end;
		//opacity: 0;
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

		.cl-content {
			padding: 10rpx 30rpx;
			width: 100%;
		}

		.cl-item {
			width: 100%;
			height: 100rpx;
			line-height: 100rpx;
			border-top: 1px solid #808080;
			margin: 5rpx 0;
			flex-flow: row;
			display: flex;
			flex: 1;

			input {
				width: 60%;
				text-align: right;
				position: fixed;
				right: 10%;
				height: 60rpx;
				margin-top: 20rpx;
				// background-color: red;
				color: #808080;
			}

			text {
				position: fixed;
				right: 5%;
			}
		}

		.cl-item-name {
			margin-left: 20rpx;
		}

		.cl-pic-item {
			height: 120rpx;
			line-height: 120rpx;

		}

		.cl-item-desc {
			height: 200rpx;

			view,
			text {
				line-height: 200rpx;
			}

			textarea {
				width: 50%;
				text-align: right;
				position: fixed;
				right: 10%;
				height: 180rpx;
				line-height: 30rpx;
				font-size: 30rpx;
				margin-top: 20rpx;
				// background-color: red;
				color: #808080;
			}

		}

		.choose-image {
			padding: 0 !important;
			width: 100rpx;
			height: 100rpx;
			// position: fixed;
			// right: 10%;
			margin-right: 10%;
			margin-top: 10rpx;
			border-radius: 15rpx;

			//overflow: hidden;
			image {
				width: 100rpx;
				height: 100rpx;

			}
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
