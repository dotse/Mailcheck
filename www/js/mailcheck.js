//  Mailcheck javascript code
//

$(document).ready(function() {
	init();
});

function init()
{
	$('#language').change(function() {
		var lang = $('#language option:selected').val();
		$.post('/', {action: 'lang', lang: lang}, function(resp) {
			if (resp == "ok")
				window.location = window.location;
		});
	});
}

function startTest(email, extra)
{
	if ($('#testnow').hasClass('button-disabled'))
		return;
	
	if (validateEmail(email) == false)
	{
		$('#error_box').hide().slideDown();
		return false;
	}

	$('#testnow').removeClass('button-enabled').addClass('button-disabled');

	$('#error_box').hide();

	var data = 'email=' + email;
	if (extra != '')
		data += '&extra=' + extra;
	if ($('#slow-tests').is(':checked'))
		data += '&slow-tests=true';

	$.ajax({
		type: 'POST',
		url: '/ajax/start-test.php?t=' + Math.floor(new Date().getTime()/1000),
		data: data,
		dataType: 'json',

		success: function(json){
			if (json['state'] == 'DENIED')
			{
				$('#result_status').hide().slideDown();
				showStatusDialog('error', Translations.denied.header2, json.message, json.custom);
				setTimeout('enableButton();', 300 );
				return false;
			}
			else if (json['state'] == 'WAITING_INPUT')
			{
				var body = json.start_time+'-'+json.test_id;
				var subject = 'This is mailcheck';
				g_response = json;
				$('#d2-mailto-link').attr('href', 'mailto:'+json.emails+'?subject='+subject+'&body='+ body);
				$('#d3-subject').html(subject);
				$('#d3-email').html(json.emails.replace(',', ', '));
				$('#d3-body').html(body);
				$('#slow-tests-checkbox').hide();
				$('#testbutton').hide();
				$('#dialog_1').slideDown();
				return false;
			}
			else if (json['state'] == 'INVALID_EMAIL')
			{
				$('#error_box').show();
				setTimeout('enableButton();', 300 );
				return false;
			}
	
			document.location = '/result/' + json.start_time + '-' + json.test_id;
		}
	});

	return false;
}

function emailsSent()
{
	if (g_response == false)
		return false;
	
	var data = 'test_id='+g_response.test_id+'&start_time='+g_response.start_time;
	$.ajax({
		type: 'POST',
		url: '/ajax/emails-sent.php',
		data: data,
		dataType: 'json',

		success: function(json){

			if (json.state == 'QUEUED')
			{
				document.location = '/result/' + json.start_time + '-' + json.test_id;
			}
		}
	});
}

function enableButton()
{
	$('#testnow').removeClass('button-disabled').addClass('button-enabled');
}

function Test()
{
	var self = this;

	self.init = function()
	{
		self.lastResult = 0;
		self.refreshRate = 3000;

		self.testStatus = 0;
		self.goldStars = 0;
	}

	self.getDomain = function()
	{
		return self.domain;
	}

	self.setDomain = function(domain)
	{
		self.domain = domain;
	}

	self.getTestID = function()
	{
		return self.testId;
	}
	
	self.getTime = function()
	{
		return self.time;
	}

	self.resetView = function()
	{
		$('#listdiv').empty();
		$('#treediv').empty();
		activateSimpleTab();
	}

	self.getTest = function(id, time)
	{
		self.testId = id;
		self.time = time;
		
		self.resetView();
		$("#resultwrapper").slideDown('fast');

		var u = parseInt(new Date().getTime() / 1000);
		var params = {test: id, u: u, time: time, last_result: self.lastResult};
		$.getJSON('/getTestResult.php', params, function(response) {
			self.setDomain(response.domain);
			g_history.showHistory(1);
			self.getResult(response);
		});
	}

	self.getResultData = function(id, time)
	{
		self.testId = id;
		self.time = time;

		var u = parseInt(new Date().getTime() / 1000);
		var params = {test: id, u: u, time: time, last_result: self.lastResult};
		$.getJSON('/getTestResult.php', params, function(response) {
			self.setDomain(response.domain);
			self.getResult(response);
		});
	}

	self.getResult = function(response)
	{
		if (response.last_result)
			self.lastResult = response.last_result;

		if (response.status && response.status > self.testStatus)
			self.testStatus = response.status;
		if (response.gold)
			self.goldStars += response.gold;	
	
		// Add any result we got back	
		if (response.data)	
		{
			this.createStructure(response, $('#treediv'), 'basic');
			this.createStructure(response, $('#listdiv'), 'adv');
		}


		if (response.url && $('#permalink').is(':visible') == false)
		{
			$('#permalink').show();
			$('#link_to_test').html(' <a href="' + response.url + '">' + response.url + '</a>');
		}

		if (response['state'] == 'RUNNING')
		{
			if (response.message)
				showRunningBox(Translations.running.header, response.message);
		}
		else if (response.state == 'SLOW_FINISHED' || response.state == 'FINISHED')
		{
			if (response.message)
				showRunningBox(Translations.running.header, response.message);

			var message = response.domain;
			if (response.finished)
				message += ', ' + response.finished;

			// Set general test status
			if (self.testStatus == 1 && response.state == 'FINISHED')
				showStatusDialog('ok', Translations.ok.header_all, message, false, self.goldStars);
			else if (self.testStatus == 1)
				showStatusDialog('ok', Translations.ok.header, message, false, self.goldStars);
			else if (self.testStatus == 2)
				showStatusDialog('warn',Translations.warning.header, message, false, self.goldStars);
			else if (self.testStatus == 3)
				showStatusDialog('error',Translations.error.header, message, false, self.goldStars);
			
			// Show gold box 
			if (self.goldStars > 0)
			{
				$('#status_gold_count').html(self.goldStars);
				$('#status_gold').show();
			}
	
			self.refreshRate = 20000;

			if (response.state == 'FINISHED')
			{
				$('#result_running').hide();
				return;
			}
		}
		else if (response['state'] == "QUEUED")
		{
			showStatusDialog('load', Translations.queued.header, Translations.queued.label);
		}
		else if (response['state'] == 'DENIED')
		{
			showStatusDialog('error', Translations.denied.header, response['domain']);
			return;
		}
		else if (response['state'] == 'NOT_FOUND')
		{
			showStatusDialog('error', Translations['notFound']['header'], Translations['notFound']['label']);
			return;
		}
	
		setTimeout('g_test.getResultData(' + self.testId + ',' + response['time'] +');', self.refreshRate);
	}

	self.createStructure = function(response, list, type)
	{
		// cats
		$.each(response.data, function(category, category_data){
			if ($('#category_'+type+'_'+category).length == 0)
			{
				var cat = '<div id="category_'+type+'_'+category+'"><div class="maintest"><h4 id="cat_'+type+'_'+category+'" class=""><a id="cat_link_'+type+'_'+category+'" class="open">'+category_data.category+'</a></h4></div><div id="rows_'+type+'_'+category+'"></div></div>';
				list.append(cat);
				$('#cat_link_'+type+'_'+category).bind('click', function() {
					var id = this.id.split('_');
					if ($(this).hasClass('closed'))
					{
						$(this).removeClass('closed').addClass('open');
						$('#rows_'+id[2]+'_'+id[3]).show();
					}
					else
					{
						$(this).removeClass('open').addClass('closed');
						$('#rows_'+id[2]+'_'+id[3]).hide();
					}
				});
			}
			

			if (category_data.status > classToStatus($('#cat_'+ type + '_' + category).attr('class')))
				$('#cat_'+type+'_'+category).attr('class', statusToClass(category_data.status));
		
			// tests
			$.each(category_data.data, function(plugin, plugin_data) {
				var group_div = '<div style="display: none" id="test_'+type+'_'+plugin+'"><ul class="subtests"><li class="subtestcat"><p class="'+statusToClass(plugin_data.status)+'">' + plugin_data.plugin + '</p></li>';

				var recommendation = null;
				$.each(plugin_data.data, function(row, data) {
					var status = statusToClass(data.status);
					
					if (data.gold == 1) // gold star
						status = "gold";
					if (data.status == -2) // recommendation
						recommendation = data.message;
					else if (data.status == -3) // extra-link
						group_div += '<li class="lev2 extra"><p class=""><a href="'+data.message+'" target="_blank">'+data.message+'</a></p></li>';
					else if (data.status == -4) // extra
					{
						if (data.type == type || data.type == 'all')
							group_div += '<li class="lev2 extra"><p class="">'+data.message+'</p></li>';
					}

					else if (data.type == 'all' || data.type == type)
						group_div += '<li class="lev2"><p class="'+status+'">'+data.message+'</p></li>';
				});
				if (recommendation != null)
					group_div += '<li class="lev2"><p class="recommendation">'+recommendation+'</p></li>';

				group_div += '</ul></div>';
				$('#rows_'+type+'_'+category).append(group_div);
				
				// HAX for stupid IE 7
				$('#test_'+type+'_'+plugin).fadeIn(function(){
					if ($.browser.msie)
					    this.style.removeAttribute("filter");
				});
			});
		});
	}
}

function History()
{
	var self = this;
	var currentPage = 0;
	var totalPages = 1;

	self.init = function()
	{
		$("#pagerstart").bind('click', self.firstPage);
		$("#pagerback").bind('click', self.prevPage);
		$("#pagerforward").bind('click', self.nextPage);
		$("#pagerend").bind('click', self.lastPage);
	}

	self.firstPage = function()
	{
		if (1 < currentPage)
			return self.showHistory(1);
	}

	self.nextPage = function()
	{
		if (currentPage < totalPages)
			return self.showHistory(currentPage + 1);
	}

	self.prevPage = function()
	{
		if (1 < currentPage)
			return self.showHistory(currentPage - 1);
	}

	self.lastPage = function()
	{
		if (currentPage < totalPages)
			return self.showHistory(totalPages);
	}

	self.showHistory = function(page)
	{
		$('#history_loader').show();

		var domain = g_test.getDomain();
		var test = g_test.getTestID();
		var time = g_test.getTime();
		$.getJSON('/getHistory.php', {domain: domain, page: page, test: test, time: time}, function(response) {

			if (!response.data)
				return;

			var pagerList = $("#pagerlist")[0];
			while (0 < pagerList.childNodes.length) 
				pagerList.removeChild(pagerList.childNodes[0]);

			var historyCount = 0;
			$.each(response.data, function(k,v) {
				historyCount++;

				var li = $(document.createElement('li'));
				var a = $(document.createElement('a'));
				a.attr('href', v.url).addClass(v.className).html(v.started);

				li.append(a);
				$('#pagerlist').append(li);
			});

			if (historyCount > 0)
				$('#pager_no_hitory').hide();
			else
				$('#pager_no_history').show();

			currentPage = parseInt(response.current_page);
			totalPages = parseInt(response.pages);
			$("#pagerlabel")[0].innerHTML = response.current_page + "/" + response.pages;
			$("#pagerstart").attr("src", "/images/pager_start_" + ((1 < currentPage) ? "on" : "off") + ".png");
			$("#pagerback").attr("src", "/images/pager_back_" + ((1 < currentPage) ? "on" : "off") + ".png");
			$("#pagerforward").attr("src", "/images/pager_forward_" + ((currentPage < totalPages) ? "on" : "off") + ".png");
			$("#pagerend").attr("src", "/images/pager_end_" + ((currentPage < totalPages) ? "on" : "off") + ".png");
			
			$('#history_loader').hide();
		});
	}
}

function statusToClass(status)
{
	if (status == -2)
		return 'recommendation';
	if (status == 1)
		return 'ok';
	else if (status == 2)
		return 'warn';
	else if (status == 3)
		return 'error';
	else if (status == 4)
		return 'unknown';
	return '';
}
function classToStatus(klass)
{
	if (klass == 'recommendation')
		return -2;
	if (klass == 'ok')
		return 1;
	else if (klass == 'warn')
		return 2;
	else if (klass == 'error')
		return 3;
	else if (klass == 'unknown')
		return 4;
	return 0;
}

function activateSimpleTab()
{
	$("#simpletab")[0].className = "tab_on";
	$("#advancedtab")[0].className = "";
	$("#treediv").show();
	$("#listdiv").hide();
}

function activateAdvancedTab()
{
	$("#simpletab")[0].className = "";
	$("#advancedtab")[0].className = "tab_on";
	$("#treediv").hide();
	$("#listdiv").show();
}

// type = load, error, ok, warn
function showStatusDialog(type, header, label, custom, gold)
{
	if (custom == true)
	{
		$('#status_customMessage').show().html(label);
		$('#status_header').hide();
		$('#status_text').hide();
	}
	else
	{
		if (gold == undefined || gold <= 0)
		{
			$('#status_customMessage').hide();
			$('#status_header').html(header).show();
			$('#status_text').html(label).show();
		}
		else
		{
			$('#status-gold-customMessage').hide();
			$('#status-gold-header').html(header).show();
			$('#status-gold-text').html(label).show();
		}
	}

	if (gold == undefined || gold <= 0)
	{
		$('#result-status-gold').hide();  $('#gold_box').hide();
		$('#status_light').attr('class', 'main' + type);
		$('#result_status').show();
	}
	else
	{
		$('#result_status').hide();
		$('#status-gold-light').attr('class', 'main' + type);
		$('#result-status-gold').show();
		$('#gold_box').show();
	}

}

function showRunningBox(header, label)
{
	if ($('#status_light').hasClass('mainload'))
		$('#result_status').hide();
	$('#running_header').html(header).show();
	$('#running_text').html(label).show();
	$('#result_running').show();
}

function validateEmail(email)
{
	var reg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,5}$/;
	return reg.test(email);
}
