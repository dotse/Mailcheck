<div id="resultwrapper" style="display: none">
	<div id="result">
		<div class="widetop">
			<img src="/images/mini-loader.gif" style="display: none" id="result_loader" alt="Loading" width="16" height="16" />
			<ul class="tabs">
				<li class="tab_on" id="simpletab"><a href="#" onclick="activateSimpleTab(); return false;"><?php echo(translate("Basic results"));?></a></li>
				<li id="advancedtab"><a href="#" onclick="activateAdvancedTab(); return false;"><?php echo(translate("Advanced results"));?></a></li>
			</ul>
		</div>
		<div id="treediv" style="display:none"></div>
		<div id="listdiv" style="display: none"></div>

		<p id="permalink" style="display:none">
			<strong><?=translate("Link to this test:")?></strong>
			<br/>
			<span id="link_to_test"></span>
		</p>
	</div>
	<div id="history">
	
		<h3 class="smalltop"><img src="/images/mini-loader.gif" style="display: none" id="history_loader" alt="Loading" width="16" height="16" /><?php echo(translate("Test history"));?></h3>
		<div class="smallbox">
			<p id="pager_error" style="display: none"><img src="/images/icon_warning.gif" alt="Error" width="16" height="14" /> <?php echo(translate("Error loading history"));?></p>
			<p id="pager_no_history" style="display: none"><?php echo(translate("No test history found"));?></p>
			<ul id="pagerlist">
				<li style="display:none"><?php echo(translate("Test history"));?></li>
			</ul>
		</div>
		
		<div class="pager" id="pagerbuttonsdiv">
			<a href="javascript:void(0);"><img src="/images/pager_start_off.png" alt="Start" id="pagerstart" /></a>
			<a href="javascript:void(0);"><img src="/images/pager_back_off.png" alt="Back" id="pagerback" /></a>
			<p><?php echo(translate("Page"));?> <span id="pagerlabel"></span></p>
			<a href="javascript:void(0);"><img src="/images/pager_forward_on.png" alt="Forward" id="pagerforward" /></a>
			<a href="javascript:void(0);"><img src="/images/pager_end_on.png" alt="End" id="pagerend" /></a>
			<div class="clear"> </div>
		</div>

		<h3 class="smalltop topmargin"><?php echo(translate("Explanation"));?></h3>
		<div class="smallbox">
			<p class="testok"><?php echo(translate("Test was ok"));?></p>
			<p class="testwarn"><?php echo(translate("Test contains warnings"));?></p>
			<p class="testerror"><?php echo(translate("Test contains errors"));?></p>
			<p class="testoff"><?php echo(translate("Test was not performed"));?></p>
			<p class="testgold"><?php echo(translate("Gold star awarded"));?></p>
			<p class="testrecommend"><?php echo(translate("Recommendation"));?></p>
		</div>

	</div>
</div>
<script type="text/javascript">
<!--
	g_test.getTest('<?=$this->testId?>', <?=$this->time?>);
	showStatusDialog('load', Translations.loading.header, Translations.loading.label);
-->
</script>
