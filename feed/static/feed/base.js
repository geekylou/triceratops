if ('serviceWorker' in navigator) { 
  navigator.serviceWorker.register('/service-worker.js').then(
  function(registration) {
    console.log("success!");
    if (registration.installing) {
      registration.installing.postMessage("Howdy from your installing page.");
    }
  },
  function(why) {
    console.error("Installing the worker failed!:", why);
  });
}
function showOfflineAlert(err)
{
    var content = document.getElementById("alerts-content");  
    content.innerHTML='<div class="alert alert-danger" role="alert">'+err+'</div>';
    return null;
}
 
function showDismissibleAlert(type,message)
{
    var content = document.getElementById("alerts-content");  
    content.innerHTML='<div class="alert alert-'+type+' alert-dismissible" role="alert">\
                       <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                       '+message+'</div>';
}

function addArguments(uri,args)
{
    if(uri.endsWith('?') || uri.indexOf('?') > 0)
    {
        return uri+'&'+args;
    }
    return uri+'?'+args;
}

function find_tag(tag,tag_name)
{
  var container = tag;
  while(container)
  {
    var container_args = container.className.split(' ');
    if(container_args[0] == tag_name)
    {
      return container;
    }
    container = container.parentNode; 
  }
  return undefined;
}

function myFunction(evt) {
    var container = evt.target;
    var index;
    while(container)
    {
      var container_args = container.className.split(' ');
      if(container_args[0] == 'panel')
      {
        break;
      }
      container = container.parentNode; 
    }
    for (index=0; index < container.children.length; index=index+1)
    {
      if(container.children[index].className.split(' ')[0] =='panel-body')
      {
        container = container.children[index];
        break;
      }
    }
    //var container = evt.path[3].children[1];
    if(container.style.maxHeight==="")
    {
      container.style.maxHeight="300px";
      evt.target.textContent="+";
    }
    else
    {
      container.style.maxHeight="";
      evt.target.textContent="-";
    }
}

function loadContentLink(evt)
{
var url = evt.currentTarget.href;
if (url.startsWith(window.location.origin+'/rss'))
  {
    fetch(addArguments(url,'&no_header'),
    {
      credentials: 'include'
    }).then(function(responseObj)
    {
      document.getElementById("alerts-content").innerHTML='';
      return responseObj.text();
    },showOfflineAlert
    ).then(function(text) 
    {
      var content = document.getElementById("content");
      content.innerHTML=text;
      editor.setVisibility(false);
      editor.reset();
    });
    history.replaceState( {} , 'rss', url );
    return false;
  }
  return true;
}

var next_div=null;

function loadMoreLink(evt)
{
  if (next_div === null)
  {
      next_div = document.createElement("div");
      var feed = document.getElementById("content");
      feed.appendChild(next_div);
  }
var url = document.getElementById("nextUrl").href;
fetch(url+'&no_header',
{
  credentials: 'include'
}).then(function(responseObj) 
{
  //console.log('status: ', responseObj.status);
  return responseObj.text();
},showOfflineAlert).then(function(text) 
{
  //console.log('html: ', text);
  if (next_div !== null && text !== null)
  {
    var overflow = document.getElementById("overflow");
    next_div.innerHTML=text;
    next_div=null;
    overflow.parentNode.removeChild(overflow);
  }
});
return false;
}

function likeLink(evt)
{
    var form=evt.currentTarget.parentNode;
    fetch(base_url+'action', {
	method: 'post',
    credentials: 'include',
	body: new FormData(form)
 }).then(function(responseObj) 
{
  if (responseObj.status !== 200) 
  {
    console.log('status: ', responseObj.status);
    responseObj.text().then(function(text)
    {
      console.log('html: ', text);
    });
  }
  else responseObj.json().then(function(json) 
  {
    //console.log('html: ', json);
    var element = form.getElementsByTagName("span");
    //console.log(form[0]);
    var liked = json["liked"];
    if (liked == "1")
    {
      element[0].style.color="orange";
      form[0].value="0";
    }
    else
    {
      element[0].style.color="";
      form[0].value="1";
    }
  });  
},showOfflineAlert);
return false;
}

function toggleEditor(event)
{
  editor.toggleVisibility(true);
}

var editor = (
    function() {
    var editor_url = base_url+'action';
    var update = false;
    var visible_after_post = true;
    var reset_editor = false;
    function reset()
    {
        editor_url = base_url+'action';
        update = false;
	visible_after_post = true;
	reset_editor = true;
    }
    
    function sendPost(evt)
    {
        var form=evt.currentTarget.parentNode.parentNode.parentNode;
        
        var form_data = new FormData(form);
        
        if (update)
        {
            form_data.set('action','update');
        }
        
        form_data.set('description',simplemde.value());
        console.log(editor_url);
        fetch(editor_url, {
        method: 'post',
        credentials: 'include',
        body: form_data,
     }).then(function(responseObj) 
    {
        responseObj.json().then(function(text)
        {
          console.log('html: ', text);
          var next_div = document.createElement("div");
          var content = document.getElementById("content");
          next_div.innerHTML=text['html'];
          content.insertBefore(next_div, content.firstChild);
          simplemde.value("");
          setVisibility(visible_after_post);
        });
    },showOfflineAlert);
    return false;
    }

    function editPost(evt)
    {
        var form=evt.currentTarget.parentNode;
        
        var form_data = new FormData(form);
        fetch(addArguments(form.attributes.action.value,'json&no_header'), {
        method: 'post',
        credentials: 'include',
        body: form_data,
     }).then(function(responseObj) 
    {
        responseObj.json().then(function(text)
        {
	  reset_editor = false; // Don't reset the editor when it becomes visible!
          console.log('html: ', text);
          var editor_submit_button = document.getElementById('editor-submit-button');
          editor_submit_button.innerHTML = '<span class="glyphicon glyphicon-save" aria-hidden="true"></span> Update';
          setVisibility(true);
          simplemde.value(text.post.description);
          document.getElementById('editor-title').value=text.post.title;
          update = true;
          editor_url = addArguments(form.attributes.action.value,'json&no_header');
          // show editor
          //form.style.display = 'none';
          visible_after_post = false;
          
          var panel_base = document.getElementById('panel-base');
          panel_base.parentNode.removeChild(panel_base);
        });
    },showOfflineAlert);
    return false;
    }
    
    function setVisibility(visible)
    {
        if (visible)
        {
             document.getElementById('editor-panel').style.display = 'block';
	     if (reset_editor)
	     {
	       simplemde.value("");
	       var editor_submit_button = document.getElementById('editor-submit-button');
	       editor_submit_button.innerHTML = '<span class="glyphicon glyphicon-save" aria-hidden="true"></span> Post';
	       document.getElementById('editor-title').value="";
	       reset_editor = false;
	     }
        }
        else
        {
            document.getElementById('editor-panel').style.display = 'none';
        }
    }

    function toggleVisibility()
    {
       setVisibility(document.getElementById('editor-panel').style.display=='none');
    }
    
    return {
    editPost: function(evt) {
      editPost(evt);
    },
    sendPost: function(evt) {
     sendPost(evt);
    },
    setVisibility: function(visible) {
     setVisibility(visible);
    },
    toggleVisibility: function() {
     toggleVisibility();
    },
    reset: function() {
     reset();
    }
    };
    })();
    
function sendPost(evt)
{
   editor.sendPost(evt);
}
function deletePost(evt)
{
    var form=evt.currentTarget.parentNode;
    fetch(base_url+'action', {
	method: 'post',
    credentials: 'include',
	body: new FormData(form)
 }).then(function(responseObj) 
{
  if (responseObj.status !== 200) 
  {
    console.log('status: ', responseObj.status);
    responseObj.text().then(function(text)
    {
      console.log('html: ', text);
    });
  }
  else responseObj.json().then(function(json) 
  {
    console.log('html: ', json);
    if (json.deleted)
    {
        var panel_base = document.getElementById('panel-base');
        panel_base.parentNode.removeChild(panel_base);
        showDismissibleAlert('success','post deleted!');
    }
  });  
},showOfflineAlert);
return false;
}

