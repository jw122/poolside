function loadNewListings(app){
  $.ajax({
            url: "/api/new-listings",
            type: "GET",
            cache: false,
            success: function(response) {
              app.newListings = response.tokens;
            }
      });
}

function loadTopMovers(app){
  $.ajax({
            url: "/api/top-movers",
            type: "GET",
            cache: false,
            success: function(response) {
              app.topMovers = response.tokens;
            }
      });
}

$(function(){

  var app = new Vue({
  el: '#tokens',
  delimiters: ['${', '}'],
  data: {
    newListings: [],
    topMovers: []
  }
});

loadNewListings(app);
loadTopMovers(app);

});
