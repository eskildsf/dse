(function($) {
	$.fn.charCount = function(){
	
		function calculate(obj){
			var count = $(obj).val().length;
                        // The first 160 characters cost 0.6 kr.
                        // Every additional 140 characters cost 0.3 kr.
                        var price = 0;
                        if ( count > 0 ) {
                        price = price + 0.6;
                        }
                        if ( count > 160 ) {
                        price = price + Math.ceil((count-160)/140)*0.3;
                        }
			$(obj).next().html('Characters: ' + count + '<br />Price: ' + price.toFixed(2) + ' kr/message');
		};
		
		this.each(function() {  			
			$(this).after('<p>Characters: </p>');
			calculate(this);
			$(this).keyup(function(){calculate(this)});
			$(this).change(function(){calculate(this)});
		});
	};
})(jQuery);


$(document).ready(function(){
	$(".counted").each(function(){$(this).charCount();});
});
