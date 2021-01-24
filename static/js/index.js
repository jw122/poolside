function loadNewListings(app){
  $.ajax({
            url: "/api/new-listings",
            type: "GET",
            cache: false,
            success: function(response) {
              $.poolside.newListings = response.pairs;
            }
      });
}

function loadTopMovers(app){
  $.ajax({
            url: "/api/top-movers",
            type: "GET",
            cache: false,
            success: function(response) {
              $.poolside.topMovers = response.tokens;
            }
      });
}

function searchBar(){
    var minlength = 3;
   $("#search-bar-input").keyup(function () {
       var that = this,
       value = $(this).val();

       if (!value.length){
          $.poolside.searchResults = [];
          return;
       }

       if (value.length >= minlength ) {
           if ($.searchRequest != null)
               $.searchRequest.abort();
           $.searchRequest = $.ajax({
               type: "GET",
               url: "/api/search",
               data: {
                   'keyword' : value
               },
               success: function(response){
                   $.poolside.searchResults = response.tokens;
               }
           });
       }
   });
}

$(function(){

  $.poolside = new Vue({
  el: '#tokens',
  delimiters: ['${', '}'],
  data: {
    isAdmin: $.isAdmin,
    newListings: [],
    topMovers: [],
    searchResults: []
  }
});

loadNewListings();
loadTopMovers();

searchBar();

$('#tokens').click(function(e){
  var parent = $(e.target).parent();
  if (parent.hasClass('admin-action')){
    $.ajax({
        type: "POST",
        url: "/admin/admin-action",
        data: {
            'action' : parent.attr('data-action'),
            'pair': parent.parents('td').attr('data-token')
        },
        success: function(response){
          loadNewListings();
        }
    });

  }
});

});
