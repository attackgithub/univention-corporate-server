function HTTPClient(){}HTTPClient.prototype={url:null,request:null,callInProgress:false,userhandler:null,init:function(a){this.url=a;try{this.request=new XMLHttpRequest()}catch(d){var c=["MSXML2.XMLHTTP.4.0","MSXML2.XMLHTTP.3.0","MSXML2.XMLHTTP","Microsoft.XMLHTTP"];var f=false;for(var b=0;b<c.length&&!f;b++){try{this.request=new ActiveXObject(c[b]);f=true}catch(d){}}if(!f){throw"Unable to create XMLHttpRequest."}}},asyncGET:function(b){if(!this.request){return false}if(this.callInProgress){throw"Call in progress"}this.callInProgress=true;this.userhandler=b;this.request.open("GET",this.url,true);var a=this;this.request.onreadystatechange=function(){a.stateChangeCallback(a)};this.request.send(null)},stateChangeCallback:function(b){switch(b.request.readyState){case 1:try{b.userhandler.onInit()}catch(c){}break;case 2:try{status=b.request.status;if(status!=200){b.userhandler.onError(status,b.request.statusText);b.request.abort();b.callInProgress=false}}catch(c){}break;case 3:try{var a;try{a=b.request.getResponseHeader("Content-Length")}catch(c){a=NaN}b.userhandler.onProgress(b.request.responseText,a)}catch(c){}break;case 4:try{b.userhandler.onLoad(b.request.responseText)}catch(c){}finally{b.callInProgress=false}break}}};