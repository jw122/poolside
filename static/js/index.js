function loadNewListings(){
  $.ajax({
            url: "/api/new-listings",
            type: "GET",
            cache: false,
            success: function(response) {
              $.poolside.app.newListings.data = response.pairs;
              $.poolside.app.setPages($.poolside.app.newListings);
            }
      });
}

function loadTopMovers(){
  $.ajax({
            url: "/api/top-movers",
            type: "GET",
            cache: false,
            success: function(response) {
              $.poolside.app.topMovers.data = response.tokens;
              $.poolside.app.setPages($.poolside.app.topMovers);
              loadAavegotchis();
            }
      });
}

function loadAavegotchis(){
  $.ajax({
            url: "/api/aavegotchis",
            type: "GET",
            cache: false,
            success: function(response) {
              console.log(response);
              $.poolside.app.aavegotchis = response.aavegotchis.map(a => {
                a.renderKey = a.id;
                return a;
              });
              $.poolside.app.aavegotchis.forEach((e, i) =>
              $.poolside.fetchAavegotchiSvgs(i));
            }
      });
}

function searchBar(){
    var minlength = 3;
   $("#search-bar-input").keyup(function () {
       var that = this,
       value = $(this).val();

       if (!value.length){
          $.poolside.app.searchResults = [];
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
                   $.poolside.app.searchResults = response.tokens;
               }
           });
       }
   });
}

$(function(){

  $.poolside = {};
  $.poolside.app = new Vue({
  el: '#tokens',
  delimiters: ['${', '}'],
  data: {
    isAdmin: $.isAdmin,
    newListings: {
      data: [],
      page: 1,
			perPage: 10,
			pages: [],
    },
    topMovers: {
      data: [],
      page: 1,
			perPage: 10,
			pages: [],
    },
    searchResults: [],
    aavegotchis: []
  },
  components: {
    	'carousel': VueCarousel.Carousel,
      'slide': VueCarousel.Slide
  },
  methods:{
  		setPages (list) {
        list.pages = [];
  			let numberOfPages = Math.ceil(list.data.length / list.perPage);
  			for (let index = 1; index <= numberOfPages; index++) {
  				list.pages.push(index);
  			}
  		},
  		paginate (list) {
  			let page = list.page;
  			let perPage = list.perPage;
  			let from = (page * perPage) - perPage;
  			let to = (page * perPage);
      	return  list.data.slice(from, to);
  		}
  	},
  	computed: {
  		displayedNewListings () {
  			return this.paginate(this.newListings);
  		},
      displayedTopMovers () {
  			return this.paginate(this.topMovers);
  		}
  	},
  	created(){
      loadNewListings();
      loadTopMovers();
      $('#tokens').removeClass('invisible');
  	},
  	filters: {
  		trimWords(value){
  			return value.split(" ").splice(0,20).join(" ") + '...';
  		}
  	}
  })

  $.poolside.quote = new Vue({
    el: '#quotes',
    delimiters: ['${', '}'],
    data: {
      quoteInfo: []
    },
  })




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

  if (parent.hasClass('token-description-overview')){
      console.log('clicked');
      parent.addClass('hidden').parent().find('.token-description-detailed').removeClass('hidden');
  }
  if (parent.hasClass('token-description-detailed') || $(e.target).hasClass('token-description-detailed'))  {
    var td = $(e.target).parents('td:first');
    td.find('.token-description-detailed').addClass('hidden');
    td.find('.token-description-overview').removeClass('hidden');
  }

});

$('#one-inch-quote').click(function(e) {
  console.log("getting 1inch quote!")
  token1 = document.getElementById('from-token-address').innerHTML;
  token2 = document.getElementById('to-token-address').value;
  if (token1 == token2) {
    // fromTokenAddress and toTokenAddress cannot be the same
    return;
  } else {
    amount = document.getElementById('quote-amount').value;
    request_url = '/api/one-inch/' + token1 + '-' + token2 + '-' + amount
    $.ajax({
      type: "GET",
      url: request_url,
      success: function(response){
        console.log("response: ", response.quotes)
        $.poolside.quote.quoteInfo = response.quotes;
      }
    })
  }

})

});
