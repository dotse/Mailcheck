<div class="breadcrumb">
	<a href="/admin">Admin</a> > <a href="/admin/bugreports.php?list">Bug reports</a> > Report
</div>

<div>
	<div style="padding-bottom: 5px"><span class="bold">Reported by:</span> "<?=$this->report['email']?>"<span class="bold">, at:</span> <?=substr($this->report['created'],0,19)?></div>
	<div class="bold">Description:</div>
	<div><?=nl2br($this->report['description'])?></div>
</div>
