/* Runs inside the hidden iframe created by Auth.codeFromHiddenFrame().
   Keycloak redirects here with ?code=...&state=... on success, or
   ?error=login_required&state=... when prompt=none cannot be satisfied.
   Either way we hand the result to the parent and do nothing else. */
(function(){
  var q = new URLSearchParams(location.search);
  var code  = q.get("code");
  var state = q.get("state");
  var error = q.get("error");
  if(!code && !error) error = "callback reached with no code";
  var target = window.parent && window.parent !== window ? window.parent : window.opener;
  if(!target) return;
  try{
    target.postMessage({ type:"eda-snake-auth", state:state, code:code, error:error },
                       location.origin);
  }catch(e){ /* nothing useful to do here */ }
})();
