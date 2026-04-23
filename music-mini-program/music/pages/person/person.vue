<template>
	<view class="person">
		<view class="container">
			<view class="user">
				<view class="user-pic">
					<image :src="userinfo.userpic" mode="aspectFill"></image>

					<!-- <open-data type="userAvatarUrl"></open-data> -->

				</view>
				<view class="user-text">
					<!-- <open-data type="userNickName"></open-data> -->
					<view class="user-text-name">{{userinfo.nickName}}</view>
					<button @tap="openInfo" class="user-text-edit">编辑信息</button>
				</view>
			</view>
			<view class="mylike">
				<view class="mylike-item" @tap="handleToMylike">
					<view class="mylike-item-img">
						<image src="../../static/mylike.png"></image>
					</view>
					<view class="mylike-item-text">
						<view>我喜欢的音乐</view>
						<view>{{likeNumber}}首</view>
					</view>
				</view>
			</view>
			<view class="mylist">
				<view class="mylist-box">
					<view class="mylist-title">
						自建歌单({{selflists.length}}个)
						<text class="iconfont icon-add" @tap="openCreateWindow('新建歌单',null)"></text>
					</view>
					<scroll-view scroll-y="true">
						<view class="mylist-item" v-for="(item,index) in selflists" :key="index"
							@tap="handleToSelflist(item.id)">
							<view class="mylist-item-img">
								<image mode="aspectFill" :src="item.coverPic"></image>
							</view>
							<view class="mylist-item-text">
								<view>{{item.name}}</view>
								<view>{{item.songSize}}首</view>
							</view>
							<view class="mylist-item-op">
								<text class="iconfont icon-edit" @tap.stop="eidtSelflist(index)"></text>
								<text class="iconfont icon-delete" @tap.stop="deleteSelflist(item.id)"></text>
							</view>
						</view>
					</scroll-view>
				</view>
			</view>
			<view class="logout">
				<button class="logout-btn" @tap="logout">退出登录</button>
			</view>
		</view>
		<!-- 		<view v-if="infoShow">
			<personInfo title="个人信息" ></personInfo>
		</view> -->
		<!-- <personInfo></personInfo> -->

		<!-- 创建歌单 -->
		<!--  -->
		<createSelflist :selflist="listinfo" :title="selflistTitle" :createShow="createShow"
			@changeShowCreate="changeShowCreate"></createSelflist>
		<!-- 个人信息 -->
		<view class="personInfo" :class="{show:show}">
			<view @tap="closeInfo()" class="mask" bind:tap="cancel" catch:touchmove="emptyHandler"></view>
			<view class="container ">

				<view class="title">
					个人信息
				</view>
				<view class="close-box" @tap="closeInfo()" bind:tap="cancel">
					<text class="iconfont icon-cancel"></text>
				</view>
				<view class="info-content">
					<view class="info-item info-pic-item">
						<view class="info-item-name">头像</view>

						<button class="avatar-wrapper" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
							<!--  @tap="changeUserPic" -->
							<image mode="aspectFill" class="avatar" :src="getavatar"></image>
						</button>
						<!-- 	</view> -->
						<text class="iconfont icon-right"></text>
					</view>
					<view class="info-item">
						<view class="info-item-name">昵称</view>
						<input @blur="getNickname" type="nickname" v-model="getnickname" name="getnickname" />
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
		<footermusic bottom="125rpx"></footermusic>
		<tabbar :selected="selected"></tabbar>
	</view>
</template>

<script>
	import tabbar from '../../components/tabbar/tabbar.vue'
	import createSelflist from '../../components/createSelflist/createSelflist.vue'
	import footermusic from '../../components/footermusic/footermusic.vue'
	import {
		thisUrl
	} from '../../common/config.js'
	import {
		getUser,
		updateUser,
		getSelflistsOfUser,
		deleteSelflist,
		mylikeNum
	} from '../../common/api.js'
	import {
		mapState,
		mapMutations
	} from 'vuex'
	let thisthis=null; 
	export default {
		data() {
			return {
				selected: 1,
				userinfo: {
					id: '',
					openid: '',
					sessionkey: '',
					nickName: '',
					mobile: '',
					createtime: '',
					userpic: ''
				},
				show: false,
				getnickname: '',
				getavatar: '',
				createShow: false,
				selflists: [{}], //自建歌单列表
				//传给新建/编辑歌单组件的值
				selflistTitle: '',
				listinfo: {
					id: '',
					name: '',
					coverPic: '',
					description: '',
					createUserOpenid: '',
					createDate: '',
					status: 0
				},
				likeNumber: 0,
			}
		},
		onLoad() {
			thisthis=this;
			
		},
		onShow() {
			//this.userinfo = this.$store.state.userinfo
			//this.userinfo = JSON.parse(this.$store.state.userinfo)
			this.userinfo = this.$store.state.userinfo
			if (typeof this.userinfo === 'string') {
				this.userinfo = JSON.parse(this.$store.state.userinfo)
			}
			console.log("onShow我的=" + this.userinfo)
			console.log("我的nickname=" + this.userinfo.nickName)
			this.getnickname = this.userinfo.nickName
			this.getavatar = this.userinfo.userpic
			//获取用户自建歌单
			getSelflistsOfUser(this.userinfo.openid).then(res => {
				if (res != null) {
					thisthis.selflists = res;
					//console.log("获取自建歌单"+this.selflists)
				}
			})
			//获取收藏曲数
			mylikeNum(this.userinfo.openid).then(res => {
				if (res != null) {
					this.likeNumber = res
					console.log("我的喜欢数量==" + res)
				}
			})
		},
		methods: {
			...mapMutations(['updateUserInfo', 'saveUserInfoToStorge', 'updateCheckSession', 'saveCheckSessionToStorge']),
			openInfo() {
				this.show = true;
			},
			//个人信息
			closeInfo() {
				this.show = false
			},
			//修改用户信息
			updatePersonInfo() {
				this.userinfo.nickName = this.getnickname
				this.userinfo.userpic = this.getavatar
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
				//console.log(this.userinfo.openid)
				//let userid = null;
				getUser(this.userinfo.openid).then(getuser => {
					if (getuser != null) {
						console.log("修改个人资料单项查询的getuser.id==" + getuser.id)
						this.userinfo.id = getuser.id

						console.log("修改个人资料传递信息==" + JSON.stringify(this.userinfo))
						updateUser(this.userinfo).then(updateres => {
							if (updateres != null) {
								this.updateUserInfo(updateres);

							}
						});

					}
				})
				console.log("修改个人资料后this.userinfo.id==" + this.userinfo.id)
				// user.nickName = this.userinfo.nickName;
				// user.userpic = this.userinfo.userpic;
				// user.mobile = this.userinfo.mobile;
				this.closeInfo();

			},
			//获取微信名
			getNickname(e) {
				this.getnickname = e.detail.value
				console.log(JSON.stringify(e.detail.value))
			},
			//获取微信头像
			onChooseAvatar(e) {
				let that = this;
				console.log("获取微信头像" + JSON.stringify(e.detail));
				let avatarUrl = e.detail.avatarUrl;
				uni.uploadFile({
					url: `${thisUrl}api/oss/file/fileUpload`,
					filePath: avatarUrl,
					name: "file",
					success: uploadFileRes => {
						// 根据返回的uploadFileRes.data做操作，往下逻辑要怎么写关键还是要看后端如何处理。就当前逻辑该上传接口返回的是图片需要的一个ID
						// 该方法是通过将uploadFileRes.data中的667值传参给后端，后端返回ArrayBuffer对象，最后在专程Base64字符串
						//_this.showPhoto(uploadFileRes.data)
						console.log("上传图片=" + uploadFileRes.data)
						that.getavatar = uploadFileRes.data
					}

				});
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
								url: `${thisUrl}api/oss/file/fileUpload`,
								filePath: res.tempFilePaths[0],
								name: "file",
								success: uploadFileRes => {
									// 根据返回的uploadFileRes.data做操作，往下逻辑要怎么写关键还是要看后端如何处理。就当前逻辑该上传接口返回的是图片需要的一个ID
									// 该方法是通过将uploadFileRes.data中的667值传参给后端，后端返回ArrayBuffer对象，最后在专程Base64字符串
									//_this.showPhoto(uploadFileRes.data)
									console.log("上传图片=" + uploadFileRes.data)
									that.getavatar = uploadFileRes.data
								}

							});
						}
					}
				})

			},
			//创建歌单
			changeShowCreate(createShow) { //组件传值
				this.createShow = createShow
				if (createShow == false) {
					//重新获取用户自建歌单
					getSelflistsOfUser(this.userinfo.openid).then(res => {
						if (res != null) {
							thisthis.selflists = res;
							//console.log("重新获取自建歌单" + JSON.stringify(this.selflists))
						}
					})
				}
			},
			openCreateWindow(title, listinfo) {
				console.log("创建我的歌单")
				this.selflistTitle = title;
				this.listinfo = listinfo;
				//console.log("openCreateWindow",JSON.stringify(this.listinfo))
				this.createShow = true;
			},
			//跳转到自建歌单歌曲列表页
			handleToSelflist(id) {
				console.log(id)
				uni.navigateTo({
					url: '/pages/selflist/selflist?id=' + id,
				});
			},
			//编辑歌单
			eidtSelflist(index) {
				console.log("点击编辑歌单", JSON.stringify(this.selflists[index]))
				this.listinfo = this.selflists[index];
				this.openCreateWindow("编辑歌单", this.selflists[index])
			},
			//删除歌单
			deleteSelflist(id) {
				uni.showModal({
					title: "删除",
					content: "确认删除歌单？",
					success(res) {
						if (res.confirm) {
							deleteSelflist(id).then(res => {
								if (res.statusCode == 200) {
									uni.showToast({
										title: "删除歌单成功",
										icon: "success",
										mask: true
									})
									//重新获取用户自建歌单
									getSelflistsOfUser(thisthis.userinfo.openid).then(slres => {
										if (res != null) {
											thisthis.selflists = slres;
										}
									})
								} else {
									uni.showToast({
										title: "删除歌单失败",
										icon: "fail",
										mask: true
									})
								}

							})
						}
					}
				})
			},
			//跳转至我的喜欢
			handleToMylike() {
				uni.navigateTo({
					url: '/pages/mylike/mylike?openid=' + this.userinfo.openid,
				});
			},
			//退出登录
			logout() {
				uni.showModal({
					title:'提示',
					content:'确认退出登录吗？',
					success(res) {
						if(res.confirm){
							thisthis.updateUserInfo({});
							thisthis.updateCheckSession(false);
							uni.switchTab({
								url:'../../pages/index/index'
							})
							uni.showToast({
								title: "退出登录成功",
								icon: "success",
								mask: true
							})
							
						}
					}
				})
			}
		},
		components: {
			tabbar,
			createSelflist,
			footermusic
		}
	}
</script>

<style lang="scss" scoped>


	//  用户信息
	
	// .person {

	// 	display: flex;
	// 	background-color: whitesmoke;
	// 	//height: 100vh;
	// }
	// .container{
	// 	height: 100%
	// }

	.user {
		display: flex;
		height: 220rpx;
		width: 100%;
		margin: 145rpx 30rpx 20rpx 30rpx;
		justify-content: center;
		position: relative;
	}

	.user-pic image {
		width: 150rpx;
		height: 150rpx;
		border-radius: 50%;
		position: absolute;
		left: 30rpx;
		overflow: hidden;
		//display: block;
	}

	.user-text {
		position: absolute;
		right: 60rpx;
		top: 15rpx;
		width: 68%;
		text-align: center;
		justify-content: center;
	}

	.user-text image {
		font-weight: bold;
		font-size: 40rpx;
		height: 50rpx;
		text-align: center;
		line-height: 50rpx;
		margin-bottom: 30rpx;
		justify-content: center;
	}

	.user-text-edit {
		width: 90%;
		height: 60rpx;
		border-radius: 30rpx;
		border: 1rpx solid #808080;
		line-height: 60rpx;
		font-size: 28rpx;
		color: gray;
		margin-top: 30rpx;
	}

	.mylike {
		display: flex;
		width: 100%;
		height: 120rpx;
		padding-left: 5%;
		padding-right: 5%;
		padding: 0 5% 3%% 5%;
	}

	.mylike-item {
		width: 90%;
		height: 120rpx;
		border-radius: 20rpx;
		background-color: white;
		border: 1rpx solid lightgray;
		position: relative;
		//display: flex;
	}

	.mylike-item-img,
	.mylist-item-img {
		height: 84rpx;
		width: 84rpx;
		margin-left: 24rpx;
		margin-top: 18rpx;
		border-radius: 15rpx;
		text-align: center;
		justify-content: center;
		overflow: hidden;
		/* 		position: absolute;
		left: 20rpx;
		top: 13rpx; */


	}

	.mylike-item-img image,
	.mylist-item-img image {
		width: 100%;
		height: 100%;
	}

	.mylike-item-text,
	.mylist-item-text {
		/* position: absolute;
		left: 134rpx;
		top: 13px; */
		margin-left: 140rpx;
		margin-top: -82rpx;
	}

	.mylike-item-text view:nth-child(1),
	.mylist-item-text view:nth-child(1) {
		height: 40rpx;
		line-height: 40rpx;
		font-size: 32rpx;
	}

	.mylike-item-text view:nth-child(2),
	.mylist-item-text view:nth-child(2) {
		color: #808080;
		font-size: 24rpx;
	}

	.mylist {
		display: flex;
		width: 100%;
		height: 35vh;
		padding: 0 5% 3% 5%;
	}

	.mylist-box {

		width: 90%;
		height: 100%;
		border-radius: 20rpx;
		background-color: white;
		border: 1rpx solid lightgray;
		position: relative;
	}

	.mylist-title {
		height: 120rpx;
		font-size: 35rpx;
		line-height: 120rpx;
		font-weight: bold;
		margin-left: 30rpx;

		text {
			position: fixed;
			right: 100rpx;
		}
	}

	.mylist scroll-view {
		height: 90%;
	}

	.mylist-item {
		/* 		width: 90%;
		height: 120rpx;
		border-radius: 20rpx; */
		/* position: relative; */
		margin-bottom: 38rpx;
	}

	.mylist-item-op {
		float: right;
		margin-right: 30rpx;
		margin-top: -90rpx;
		height: 100rpx;
		line-height: 100rpx;
	}

	.mylist-item-op text {
		margin-right: 30rpx;
	}
	.logout{
		height: 60rpx;
		margin-bottom: 20rpx;
	}
	.logout-btn {
		width: 90%;
		height: 60rpx;
		border-radius: 30rpx;
		border: 1rpx solid #808080;
		line-height: 60rpx;
		font-size: 28rpx;
		color: gray;
		margin-bottom: 275rpx;
	}


	/* 个人信息 */
	.personInfo {
		height:45vh;
		position: fixed;
		//top: 0;
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
			display: flex;
			flex: 1;

			input {
				width: 50%;
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

			// image {
			// 	position: fixed;
			// 	right: 10%;
			// 	margin-top: 10rpx;
			// 	width: 100rpx;
			// 	height: 100rpx;
			// 	border-radius: 50%;
			// }
		}

		.info-item-name {
			margin-left: 20rpx;
		}

		.info-pic-item {
			height: 120rpx;
			line-height: 120rpx;

		}

		.avatar-wrapper {
			padding: 0 !important;
			width: 100rpx;
			height: 100rpx;
			// position: fixed;
			// right: 10%;
			margin-right: 10%;
			margin-top: 10rpx;
			border-radius: 50%;

			//overflow: hidden;
			.avatar {
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
