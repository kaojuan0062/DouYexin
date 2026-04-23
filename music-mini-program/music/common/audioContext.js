const audioUtils = {};
var innerAudioContext = uni.createInnerAudioContext()
// var isPause = false //是否在暂停状态
// var previousSrc = '' //上一个音频的地址，如果和现在的播放地址一样就进入暂停

var isPlaying = false;
var isPlayEnd = false;
var currentTime = 0;
var currentTimeStr = '00:00';
var duration = 100;
var timeStr = '00:00';
var isChanging=false;
var thisSong={};


function getAudioContext(song){
	innerAudioContext.autoplay = false;
	//console.log("播放器函数", this.thisSong)
	innerAudioContext.src = song.url;
	innerAudioContext.onPlay(() => {
		console.log('开始播放'+innerAudioContext);
		
	});
	innerAudioContext.onCanplay(() => {
		let timeid = setInterval(() => {
			if (innerAudioContext.duration) {
				clearInterval(timeid)
				duration = innerAudioContext.duration || 0;
				console.log(duration)
				//timeStr = this.formatSecond(this.duration);
			}
		}, 500)
	});	return innerAudioContext;
}
function getIsPlaying(){
	return isPlaying;
}
function setIsPlaying(obj){
    isPlaying = obj
}
function getIsPlayEnd(){
	return isPlayEnd;
}
function setIsPlayEnd(obj){
    isPlayEnd = obj
}
function getCurrentTime(){
	return currentTime;
}
function setCurrentTime(obj){
    currentTime = obj
}
function getCurrentTimeStr(){
	return currentTimeStr;
}
function setCurrentTimeStr(obj){
    currentTimeStr = obj
}
function getDuration(){
	return duration;
}
function setDuration(obj){
    duration = obj
}
function getTimeStr(){
	return timeStr;
}
function setTimeStr(obj){
    timeStr = obj
}

module.exports = {
    getAudioContext: getAudioContext,
    getIsPlaying: getIsPlaying,
	setIsPlaying:setIsPlaying,
	getIsPlayEnd:getIsPlayEnd,
	setIsPlayEnd:setIsPlayEnd,
	getCurrentTime:getCurrentTime,
	setCurrentTime:setCurrentTime,
	setCurrentTimeStr:setCurrentTimeStr,
	getCurrentTimeStr:getCurrentTimeStr,
	getDuration:getDuration,
	setDuration:setDuration,
	getTimeStr:getTimeStr,
	setTimeStr:setTimeStr
}




