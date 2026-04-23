<template>
	<view class="music-head" :style="{color:color}">
		<view class="music-head-icon" v-if="icon">
			<text class="iconfont icon-left" @tap="handleToBack"></text> |
			<text class="iconfont icon-shouye" @tap="handleToHome"></text>
			
			
		</view>
		{{title}}
	</view>
</template>

<script>
	export default {
		name:"musichead",
		props:['title','icon','color'],
		data() {
			return {
				
			};
		},
		methods:{
			handleToBack(){
				uni.navigateBack();
			},
			handleToHome(){
				uni.switchTab({
					url:'/pages/index/index',
				});
			}
		}
	}
</script>

<style>
/* .clear{
	clear: both;
} */
.music-head{
	height: 75px;
	text-align: center;
	line-height: 75px;
	font-size: 16px;
	color: black;
	position: relative;
	overflow: hidden;
/* 	margin-top: 1%; */
	
	/* border: 1px solid red; */
}
.music-head-icon{
	width: 90px;
	height: 31px;
	background-color: rgba(0,0,0,0.4);
	border-radius: 15px;
	left:10px;
	top:25px;
	position: absolute;
	line-height: 31px;
	display: flex;
	justify-content: space-evenly;
	color: white;
	
}
</style>