<%inherit file="base.mako" />

<%def name="onload()">
    function update(){
        var oldValue = $('#total').html();
        
        $.ajax({
            url: '/live',
            dataType: 'json',
            success: function(data){
                if (oldValue != data.count) {
                    $('#total').html(data.count);
                    $('#total').animate({color: '#00A1A6'}, 250);
                    $('#total').animate({color: '#000000'}, 250);
                }
            }
        });
        setTimeout(update, 1000);
    }
    
    update();
</%def>

<section style="text-align: center">
    <h1 id="total">0</h1>
</section>