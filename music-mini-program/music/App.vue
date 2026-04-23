<script>
	
	import{mapMutations,mapState} from 'vuex'
	import {
		isExist,
		getUser
	} from 'common/api.js'
	export default {
		// data:{
		// 	songlist:[]
		// },
		onLaunch: function() {
			
			console.log('App Launch');
			uni.hideTabBar();
			//判断是否登录
			uni.checkSession({
				success: () => {
					console.log("checkSession已登录")
					this.updateCheckSession(true)
					
					//this.saveUserInfoToStorge();
					//this.getUserInfoTag=false;
					//this.closeLogin();
				},
				fail: () => {
					// this.getUserInfoTag=true;				
					// this.openLogin();
					console.log("checkSession未登录")
					this.updateCheckSession(false)
				}
			})
			//this.setSonglist(uni.getStorageSync('songlist'))
		},
		onLoad() {
			this.setSonglist(this.songlist)
			console.log("onLoad");
			//console.log("list页面存入的list==",uni.getStorageSync('songlist'))
		},
		onShow: function() {
			console.log('App Show')
			//console.log("list页面存入的list==",uni.getStorageSync('songlist'))
			uni.hideTabBar();
			this.setSonglist(this.songlist)
	
			
		},
		onHide: function() {
			console.log('App Hide')
			uni.hideTabBar();
			this.setSonglist(this.songlist)
			
		},
		onUnload:function(){
			if (this.innerAudioContext != null && this.isPlaying) {
				this.stop();
			}
		},
		computed:{
			...mapState(['ids','songlist','timeStr','innerAudioContext','isPlaying','isPlayEnd','currentTime','duration']),
		},
		methods:{
			...mapMutations(['stop','updateCheckSession','setIsPlaying', 'setThisSong', 'setSonglist']),
		}	
		
	}	
</script>

<style>
	/*每个页面公共css */
	.container{
		width: 100%;
		height: calc(100vh-75px);
		overflow: hidden;
	}
	.fixbg{
		width: 100%;
		height: 100vh;
		position: fixed;
		background-size: cover;
		background-position: center 0;
		filter: blur(5px);
		/* opacity:0.5; */
		background-image: url('./static/logo.png');
		z-index: 0;
	}
	::-webkit-scrollbar {
		display: none;
		width: 0 !important;
		height: 0 !important;
		-webkit-appearance: none;
		background: transparent;
	}
</style>
