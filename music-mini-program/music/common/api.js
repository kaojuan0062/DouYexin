import {
	baseUrl,
	thisUrl
} from './config.js'

// ===========================================================首页=========================================================
//模糊查询
export function searchSongs(key){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}song/searchSongs?key=${key}`,
			method: 'GET',
			success: res => {
				//console.log("API:searchSongs()===", res.data)
				let result = res.data
				resolve(result)
			},
			fail: (err) => {
				console.log("ERROR in searchSongs()===", err)
			}
		})
	})	
}
//热门歌单
export function topList() {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}playlist/getHotPlaylist`,
			method: 'GET',
			data: {},
			success: res => {
				// console.log(res);
				let result = res.data;
				//console.log("API:topList()===", res.data)
				resolve(result)
			},
			fail: (err) => {
				console.log(err);
			},
			complete: () => {}
		});
	});
};
//获取歌单歌曲
export function getSongs(id) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}/songsofplist/getSongList?id=${id}`,
			method: 'GET',
			data: {},
			success: res => {
				// console.log(res);
				let result = res.data;
				//console.log("API:getSongs()===", res.data)
				resolve(result)
			},
			fail: (err) => {
				console.log(err);
			},
			complete: () => {}
		});
	});
}


// export function playlist(id) {
// 	return uni.request({
// 		url: `${baseUrl}playlist/detail?id=${id}`,
// 		method: 'GET'

// 	})

// };
//获取歌单详情及歌曲，跳转到歌单list页面
export function playlist(id) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}/playlist/${id}`,

			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in playlist()===", err)
			}
		})
	})

};
//获取全部歌单
export function getTotalPlaylist(){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}/playlist/getLocalPlaylist`,
	
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in getTotalPlaylist()===", err)
			}
		})
	})
}
//轮播图
export function getBanner() {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}banner`,
			method: 'GET',
			success: res => {
				let result = res.data.content;
				resolve(result);
				// console.log("getBannerAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in getBanner()===", err)
			}
		})
	})
};

//歌手
export function getArtists() {
	return new Promise(function(resolve, reject) {
		uni.request({
			// url: `${baseUrl}artist/list`,
			url: `${thisUrl}hotartist/getHotArtist`,
			method: 'GET',
			success: res => {
				console.log("API:getArtist()===", res.data)
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in getArtist()===", err)
			}
		})
	})
}

//获取歌手详情
export function getArtistDetail(aid) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}artist/getLocalDetail?id=${aid}`,
			method: 'GET',
			success: res => {
				console.log("API:getArtistDetail()===", res.data)
				let result = res.data
				resolve(result)
			},
			fail: (err) => {
				console.log("ERROR in getArtistDetail()===", err)
			}
		})
	})
}

//获取歌手所有歌曲
export function getSongsOfAritist(aid) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}songsofartist/getLocalSongs?aid=${aid}`,
			method: 'GET',
			success: res => {
				console.log("API:getSongsOfAritist()===", res.data)
				let result = res.data
				resolve(result)
			},
			fail: (err) => {
				console.log("ERROR in getSongsOfAritist()===", err)
			}
		})
	})
}

//获取本地播放量前20
export function getTopTrackcounts(){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}song/getTopTrackcounts`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				// console.log("getBannerAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in getTopTrackcounts()===", err)
			}
		})
	})
}

//=====================================================播放页面=============================================
//当前歌曲信息
export function getThisSong(id) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}song/${id}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in getThisSong()===", err)
			}
		})
	})
}
//增加歌曲播放量
export function increaseTrackcounts(id){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}song/updateTrackcounts`,
			method: 'PUT',
			data: {
				id:id
			},
			header: {
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in increaseTrackcounts()===", err)
			}
		})
	})
}


//==========================================================登录============================================
//获取openID
export function getOpenid(code) {
	let appid = 'wxc602672091023e6e'
	let secret = '0679dc635c0455b667cb21adb4cb1766'
	let url = 'https://api.weixin.qq.com/sns/jscode2session?appid=' + appid + '&secret=' + secret +
		'&js_code=' + code + '&grant_type=authorization_code';
	return uni.request({
		url: url, // 请求路径success: result => {console.info(result.data.openid);},});}
		method: 'GET',
	});

}
//判断是否注册
export function isExist(openid) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}user/getUser?openId=${openid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in getThisSong()===", err)
			}
		})
	})
}
//注册
export function register(user) {
	console.log("登录api===", user)
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}user`,
			method: 'POST',
			data: user,
			dataType: 'json',
			header: {
				'content-type': 'application/json'
				//'content-type':'application/x-www-form-urlencoded'
			},
			success: res => {
				let result = res.data;
				resolve(result);
				console.log("api注册成功", res)
			},
			fail: (err) => {
				console.log("api注册失败", err)
			}
		})
	})
}
//=====================================================个人中心=====================================================
//查用户信息
export function getUser(openid) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}user/${openid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				//console.log("APIgetUser()===", res.data)
			},
			fail: (err) => {
				console.log("ERROR in getUser()===", err)
			}
		})
	})
}
//更新用户信息
export function updateUser(user) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}user`,
			method: 'PUT',
			data: user,
			header: {
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res.data;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in updateUser()===", err)
			}
		})
	})
}

//=====================================================自建歌单===================================================
//新建歌单
export function createSelflist(selflist){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}selflist`,
			method: 'POST',
			data: selflist,
			dataType: 'json',
			header: {
				'content-type': 'application/json'
			},
			success: res => {
				let result = res;
				resolve(result);
				console.log("新建歌单成功", res.statusCode)
			},
			fail: (err) => {
				console.log("新建歌单失败失败", err)
			}
		})
	})	
}
//查找该用户自建歌单
export function getSelflistsOfUser(openid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}selflist/getSelflist?openid=${openid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				console.log("APIgetSelflistsOfUser()===", res.data)
			},
			fail: (err) => {
				console.log("ERROR in getUser()===", err)
			}
		})
	})
}
//添加歌曲至自建歌单
export function addSongToSelflist(songid,listid,openid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}songsofselflist`,
			method: 'POST',
			data: {
				songid:songid,
				listid:listid,
				openid:openid
			},
			header: {
				//'content-type': 'application/json'
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res.data;
				resolve(result);
				console.log("新建歌单成功", res)
			},
			fail: (err) => {
				console.log("新建歌单失败失败", err)
			}
		})
	})	
}
//获取自建歌单歌曲
export function getSongsOfSelflist(id){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}songsofselflist/getSongs?id=${id}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				//console.log("API getSongsOfSelflist"+JSON.stringify(result))
			},
			fail: (err) => {
				console.log("ERROR in getSongsOfSelflist()===", err)
			}
		})
	})
}
//获取自建歌单详情
export function getSelflistDetail(id){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}selflist/${id}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				console.log("APIgetSelflistDetail()===", res.data)
			},
			fail: (err) => {
				console.log("ERROR in getSelflistDetail()===", err)
			}
		})
	})
}
//编辑歌单
export function updateSelfList(selflist) {
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}selflist`,
			method: 'PUT',
			data: selflist,
			header: {
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in updateUser()===", err)
			}
		})
	})
}
//删除歌单
export function deleteSelflist(id){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}selflist`,
			method: 'DELETE',
			data: {
				id:id
			},
			header: {
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res;
				resolve(result);
				console.log("API deleteSelflist()===", res)
			},
			fail: (err) => {
				console.log("ERROR in deleteSelflist()===", err)
			}
		})
	})
}
//从歌单中删除歌曲
export function deleteSongofSelflist(songid,listid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}songsofselflist/deleteSong`,
			method: 'DELETE',
			data: {
				songid:songid,
				listid:listid
			},
			header: {
				'content-type': "application/x-www-form-urlencoded"
			},
			success: res => {
				let result = res;
				resolve(result);
			},
			fail: (err) => {
				console.log("ERROR in deleteSongofSelflist()===", err)
			}
		})
	})
}
//=======================================================弹幕======================================================
//发送弹幕
export function createDanmu(danmu){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}danmu`,
			method: 'POST',
			data: danmu,
			dataType: 'json',
			header: {
				'content-type': 'application/json'
			},
			success: res => {
				let result = res;
				resolve(result);
				console.log("弹幕发送成功", res.statusCode)
			},
			fail: (err) => {
				console.log("弹幕发送失败", err)
			}
		})
	})	
}
//查询所有弹幕
export function getDanmus(songid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}danmu/getTotal?songid=${songid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				// console.log("getBannerAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in getDanmus()===", err)
			}
		})
	})
}

//=============================================我的喜欢====================================
//添加我的喜欢
export function addMylike(mylike){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}mylike`,
			method: 'POST',
			data: mylike,
			dataType: 'json',
			header: {
				'content-type': 'application/json'
			},
			success: res => {
				let result = res;
				resolve(result);
				console.log("歌曲收藏成功", res)
			},
			fail: (err) => {
				console.log("歌曲收藏成功", err)
			}
		})
	})	
}
//判断是否已收藏
export function isLiked(openid,songid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}mylike/isExist?openid=${openid}&songid=${songid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				console.log("isLikedAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in isLiked()===", err)
			}
		})
	})
}
//查询我的收藏
export function getMylike(openid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}mylike/likeSongs?openid=${openid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				//console.log("getMylikeAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in getMylike()===", err)
			}
		})
	})
}
//获取我的收藏个数
export function mylikeNum(openid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}mylike/likeSongsNum?openid=${openid}`,
			method: 'GET',
			success: res => {
				let result = res.data;
				resolve(result);
				//console.log("mylikeNumAPI===",result)
			},
			fail: (err) => {
				console.log("ERROR in mylikeNum()===", err)
			}
		})
	})
}
//取消收藏
export function cancelCollection(openid,songid){
	return new Promise(function(resolve, reject) {
		uni.request({
			url: `${thisUrl}mylike/cancelCollection`,
			method: 'DELETE',
			data: {
				openid:openid,
				songid:songid
			},
			header: {
				'content-type': "application/x-www-form-urlencoded",
			},
			success: res => {
				let result = res;
				resolve(result);
				console.log("API cancelCollection()===", res)
			},
			fail: (err) => {
				console.log("ERROR in cancelCollection()===", err)
			}
		})
	})
}

// //导出函数
// export default{
// 	topList,
// 	getBanner,
// 	getArtist

// }
