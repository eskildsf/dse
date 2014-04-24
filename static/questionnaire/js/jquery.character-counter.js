(function($) {
	$.fn.charCount = function(){
	
		function calculate(obj){
			var count = $(obj).val().length;
			$(obj).next().html('Characters: ' + count);
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
