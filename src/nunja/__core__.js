(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["_core_/_default_wrapper_/template.nja"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "<";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "_wrapper_tag_"), env.opts.autoescape);
output += " ";
output += runtime.suppressValue(env.getFilter("safe").call(context, runtime.contextOrFrameLookup(context, frame, "_nunja_data_")), env.opts.autoescape);
output += ">\n";
var tasks = [];
tasks.push(
function(callback) {
env.getTemplate(runtime.contextOrFrameLookup(context, frame, "_template_"), false, "_core_/_default_wrapper_/template.nja", null, function(t_3,t_1) {
if(t_3) { cb(t_3); return; }
callback(null,t_1);});
});
tasks.push(
function(template, callback){
template.render(context.getVariables(), frame, function(t_4,t_2) {
if(t_4) { cb(t_4); return; }
callback(null,t_2);});
});
tasks.push(
function(result, callback){
output += result;
callback(null);
});
env.waterfall(tasks, function(){
output += "\n</";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "_wrapper_tag_"), env.opts.autoescape);
output += ">\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
});
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
root: root
};

})();
})();
