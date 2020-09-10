$('#register').on('click', function(e){
    window.location.href = '/user/signup'
})


$(document).ready(function(){
    $('.alert').fadeIn().delay(500).fadeOut();
});

$('#back').on('click', function(e){
    window.history.back();
})

$('#back_link').on('click', function(e){
    window.history.back();
})

$('div').on('click', function(e){
    
    if (e.target.id === 'slider'){
        const parent = e.target.parentNode;
        const ind = parent.id.indexOf('f');
        const id = parent.id.substr(0,ind);
        const val = e.target.value;

        $(`#${id}rate`).text(`${val}/5`)
    };
})

$('#fav').on('click', function(e){
    e.preventDefault();

    const ind = e.target.parentNode.id.indexOf('f');
    const id = e.target.parentNode.id.substr(0,ind);

    const classes = e.target.parentNode.classList;

    if (classes.contains('fav-off')) {
        e.target.parentNode.classList.remove('fav-off')
        e.target.parentNode.classList.add('fav-on')
    } else {
        e.target.parentNode.classList.remove('fav-on')
        e.target.parentNode.classList.add('fav-off')
    }

    addFav(id);

    setTimeout(function() { get_user_favorites_page(); }, 100);
})

function get_user_favorites_page() {
    window.location.href = '/user/favorites'
}

async function addFav(id) {
    
    await axios.post('/user/favorites', {
        drinkId: id
    });
};

$('#rate_btn').on('click', function(e){
    e.preventDefault();

    const slider = e.target.nextElementSibling.nextElementSibling
    const rating = slider.value
    const ind = e.target.parentNode.id.indexOf('f');
    const id = e.target.parentNode.id.substr(0,ind);

    addRate(rating, id);

})

async function addRate(rating, id) {

    await axios.post(`/drinks/${id}`, {
        rating: rating
    });
}

$('.fav-remove').on('click', function(e){

    const ind = e.target.id.indexOf('r');
    const id = e.target.id.substr(0,ind);

    removeFav(id);

    setTimeout(function() { get_user_favorites_page(); }, 100);
})

async function removeFav(id) {
    
    await axios.post('/user/favorites', {
        drinkId: id
    });
};

$('.btn-success').on('click', function(e){

    const ind = e.target.id.indexOf('r');
    const id = e.target.id.substr(0,ind);

    window.location.href = `/user/recommend/form${id}`
})

$('.rec-remove').on('click', function(e){

    const ind = e.target.id.indexOf('r');
    const id = e.target.id.substr(0,ind);

    removeRecommend(id);

    setTimeout(function() { get_recommends_page(); }, 100);
})

async function removeRecommend(id) {
    
    await axios.post('/user/recommendations', {
        recId: id
    });
};

function get_recommends_page() {

    window.location.href = '/user/recommendations'

}