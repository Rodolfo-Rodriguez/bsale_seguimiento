
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filter Manager Class
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
class FilterManager():

	def add_filter_to_session(self, sess, field, op, value):

		filter_dict = {'field': field, 'op': op, 'value': value}

		if 'DEAL_FILTERS' not in sess:
			deal_filters = {}
		else:
			deal_filters = sess['DEAL_FILTERS']
		
		if field not in deal_filters:
			deal_filters[field] = [filter_dict]
		else:
			if filter_dict not in deal_filters[field]:
				deal_filters[field].append(filter_dict)	

		return(deal_filters)

	def remove_filter_from_session(self, sess, field, op, value):

		filter_dict = {'field': field, 'op': op, 'value': value}
		
		if 'DEAL_FILTERS' not in sess:
			deal_filters = {}
		else:
			deal_filters = sess['DEAL_FILTERS']

		if field in deal_filters:
			deal_filters[field].remove(filter_dict)
				
		return(deal_filters)

	def create_query_filter(self, sess):

		query_filter = []
		if 'DEAL_FILTERS' in sess:			
			for field, field_list in sess['DEAL_FILTERS'].items():
				if len(field_list) > 1:
					if field in ['fecha_ganado', 'fecha_pase_produccion', 'fecha_baja']:
						query_filter.append({'and':field_list})
					else:
						query_filter.append({'or':field_list})
				elif len(field_list)==1:
					query_filter.append(field_list[0])

		return(query_filter)

	def add_date_range_filter_to_session(self, sess, fecha_field, fecha_ini, fecha_fin):

		if 'DEAL_FILTERS' not in sess:
			deal_filters = {}
		else:
			deal_filters = sess['DEAL_FILTERS']
			deal_filters.clear()

		field_list = []
		if fecha_ini != '':
			field_list.append({'field': fecha_field, 'op': '>=', 'value': fecha_ini})
		if fecha_fin != '':
			field_list.append({'field': fecha_field, 'op': '<=', 'value': fecha_fin})
		deal_filters[fecha_field] = field_list

		return(deal_filters)

	def get_date_range_from_filter(self, sess, fecha_field):

		fecha_ini = ''
		fecha_fin = ''
		
		if 'DEAL_FILTERS' in sess and fecha_field in sess['DEAL_FILTERS']:
			field_list = sess['DEAL_FILTERS'][fecha_field]
			for filt in field_list:
				if filt['op'] == '>=':
					fecha_ini = filt['value']
				elif filt['op'] == '<=':
					fecha_fin = filt['value']

		return(fecha_ini, fecha_fin)
			



#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filter Manager Object
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
filter_manager = FilterManager()