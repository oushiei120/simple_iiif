import os
import glob
import re
import csv
import json
from PIL import Image

base_url = 'https://oushiei120.github.io/simple_iiif'
thum_page = 1
new_width = 240

base_title = '関西旅行'
base_credit = '関西旅行'



metadata_dict = {}
all_bib = {}
all_html_url = []
#########HTML表示画面用のメタデータ項目の設定
metadata_dict['title_ja'] = "タイトル"
metadata_dict['volume'] = "巻"
metadata_dict['author_ja'] = "著者"
metadata_dict['publisher_ja'] = "出版社"
metadata_dict['pubdate'] = "出版年"
metadata_dict['Description'] = "解題"
metadata_dict['tags'] = "タグ"
metadata_dict['isbn'] = "ISBN"
###もしほかにも日本語で表示したいものがあれば追記
'''
metadata_dict[''] = ""
metadata_dict[''] = ""
metadata_dict[''] = ""
metadata_dict[''] = ""
metadata_dict[''] = ""
'''
### IIIFの「metadata」に入れない既定の項目に関しては以下にリストしておく。
#mani_keys = ['dir','Creator','Publisher','Publication Date','Descriptopn','Notes'] 

mani_keys = ['folder','title_ja','title_en','license','attribution','within','logo','viewingHint','viewingDirection','volume','index','index_page']
with open('metadata.tsv', newline='', encoding='utf_8_sig') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t')
    rn = 0
    for row in spamreader:
        if rn == 0:
            bib_title = row
        else:
            each_bib = {}
            each_bib.update(zip(bib_title,row))
            link_name = row[0]  
            all_bib[link_name] = each_bib
        rn = rn + 1;     

#print (all_bib)
for key in all_bib.keys():
    each_manifest = {}
    all_meta = []
    skip_meta = []
    file_dir0 = key
    glob_name = key+"/*.jpg"
    if os.path.isdir(key):
        list_file_names = glob.glob(glob_name)
        for item in all_bib[key]:
            if item not in mani_keys:
                each_meta  = {} 
                item_value = all_bib[key][item]
                each_meta['label'] = item
                each_meta['value'] = item_value
                all_meta.append(each_meta)
        maniurlv2 = base_url+'/'+key+'/manifest_v2.json'
        each_manifest['@id'] = maniurlv2
        each_manifest['@type'] = 'sc:Manifest'
        each_manifest['@context'] = 'http://iiif.io/api/presentation/2/context.json' 
        each_manifest['metadata'] = all_meta
        each_manifest['attribution'] = all_bib[key]['attribution']
        each_manifest['license'] = all_bib[key]['license']
        for mani_key in mani_keys:
            if all_bib[key].get(mani_key):
                if mani_key == 'title_ja':
                    each_manifest['label'] = all_bib[key]['title_ja']
                    if 'volume' in all_bib[key]:
                        each_manifest['label'] = each_manifest['label']+' vol. '+str(all_bib[key]['volume'])
                elif mani_key == 'viewingDirection':
                    each_manifest[mani_key] = all_bib[key][mani_key]
        cn = 0
        sequence = {}
        canvases = []
        img_1st_url = ''
        #print (list_file_names)
        for file_path in list_file_names:
            service = {}
            resource = {}
            mani_image = {}
            canvas = {}
            file_dir = os.path.split(file_path)[0]
            if os.path.isdir(file_dir):
                cn = cn + 1
                canvas_number = 'p'+str(cn)+'.json'
                image_url_id = base_url+'/'+file_path
                width = 0
                height = 0
                with Image.open(file_path) as img:
                    width = img.width
                    height = img.height
                    if cn == thum_page:
                        img_1st_url =  base_url+'/'+key+'/thum.jpg'
                        aspect_ratio = height / width
                        new_height = int(new_width * aspect_ratio)
                        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                        output_image_path = key+'/thum.jpg'
                        resized_img.save(output_image_path, format="JPEG", quality=80)
                service['@context'] = 'http://iiif.io/api/image/2/context.json' 
                service['@id']  = image_url_id
                service['profile'] = 'http://iiif.io/api/image/2/level0.json'

                resource['@type'] = 'dctypes:Image'
                resource['format'] = 'image/jpeg'
                resource['width'] = width
                resource['height'] = height
                resource['@id'] = image_url_id
                #resource['service'] = service
                mani_image['@type']  = 'oa:Annotation'
                mani_image['motivation']  = 'sc:painting'
                mani_image['resource']  = resource
                mani_image['@id']  = base_url+'/'+file_dir+'/annotation/'+canvas_number
                mani_image['on']  = base_url+'/'+file_dir+'/canvas/'+canvas_number
                canvas['label'] = 'p. '+str(cn)
                canvas['images'] = []
                canvas['images'].append(mani_image)
                canvas['width'] = width
                canvas['height'] = height
                canvas['@type'] = 'sc:Canvas'
                canvas['@id'] = base_url+'/'+file_dir+'/canvas/'+canvas_number
                canvases.append(canvas)
        sequence['@id'] =  base_url+'/'+file_dir0+'/sequence/s1.json'
        sequence['@type'] =  'sc:Sequence'
        sequence['label'] =  'Current Page Order'
        sequence['canvases'] = canvases
        each_manifest['sequences'] = []
        each_manifest['sequences'].append(sequence)
        write_file_path = file_dir0+'/manifest_v2.json'
        with open(write_file_path, mode='w') as f:
            json.dump(each_manifest, f, ensure_ascii=False)

        ##ここからmanifest v3の作成#############################################
        each_manifest = {}
        all_meta = []
        skip_meta = []
        for item in all_bib[key]:
            if item not in mani_keys:
                each_meta  = {}
                each_meta['label'] = {}
                each_meta['value'] = {}
                item_value = all_bib[key][item]
                if '_ja' in item:
                    if item in metadata_dict:
                        each_meta['label']['ja'] = [metadata_dict[item]]
                        each_meta['value']['ja'] = [item_value]
                    else:
                        each_meta['label']['ja'] = [re.sub(r'_ja$','',item)]
                    eitem = re.sub(r'_ja$', '_en', item)
                    each_meta['label']['en'] = [eitem]
                    each_meta['value']['en'] = [all_bib[key][eitem]]
                    skip_meta.append(eitem)
                else:
                    if item not in skip_meta:
                        each_meta['label']['ja'] = [item]
                        each_meta['value']['ja'] = [item_value]
                        each_meta['label']['en'] = [item]
                        each_meta['value']['en'] = [item_value]
                all_meta.append(each_meta)
        maniurlv3 = base_url+'/'+key+'/manifest_v3.json'
        each_manifest['id'] = maniurlv3        
        each_manifest['type'] = 'Manifest'
        each_manifest['@context'] = 'http://iiif.io/api/presentation/3/context.json' 
        each_manifest['metadata'] = all_meta
        if 'attribution' in all_bib[key]:
            each_manifest['requiredStatement'] = {}
            each_manifest['requiredStatement']['label'] = {}
            each_manifest['requiredStatement']['value'] = {}
            each_manifest['requiredStatement']['label']['en'] = ["attribution"]
            each_manifest['requiredStatement']['label']['ja'] = ["attribution"]
            each_manifest['requiredStatement']['value']['en'] = [all_bib[key]['attribution']+', '+all_bib[key]['license']]
            each_manifest['requiredStatement']['value']['ja'] = [all_bib[key]['attribution']+', '+all_bib[key]['license']]
        elif 'attribution_ja' in all_bib[key]:
            each_manifest['requiredStatement'] = {}
            each_manifest['requiredStatement']['label'] = {}
            each_manifest['requiredStatement']['value'] = {}
            each_manifest['requiredStatement']['label']['en'] = ["attribution"]
            each_manifest['requiredStatement']['label']['ja'] = ["attribution"]
            each_manifest['requiredStatement']['value']['en'] = [all_bib[key]['attribution_en']+', '+all_bib[key]['license']]
            each_manifest['requiredStatement']['value']['ja'] = [all_bib[key]['attribution_ja']+', '+all_bib[key]['license']]
        if 'creativecommons' in all_bib[key]['license'] or 'rightsstatements.org' in all_bib[key]['license']:
            each_manifest['rights'] = all_bib[key]['license']
        for mani_key in mani_keys:
            if all_bib[key].get(mani_key):
                if mani_key == 'title_ja':
                    each_manifest['label'] = {}
                    if 'volume' in all_bib[key]:
                        all_bib[key]['title_ja'] = all_bib[key]['title_ja']+' vol. '+str(all_bib[key]['volume'])
                    each_manifest['label']['ja'] = [all_bib[key]['title_ja']]
                elif mani_key == 'title_en':
                    if 'volume' in all_bib[key]:
                        all_bib[key]['title_en'] = all_bib[key]['title_en']+' vol. '+str(all_bib[key]['volume'])
                    each_manifest['label']['en'] = [all_bib[key]['title_en']]
                elif mani_key == 'viewingDirection':
                    each_manifest[mani_key] = all_bib[key][mani_key]
        cn = 0
        sequence = {}
        canvases = []
        #print (list_file_names)
        for file_path in list_file_names:
            service = {}
            resource = {}
            mani_image = {}
            canvas = {}
            anno_page = {}
            file_dir = os.path.split(file_path)[0]
            if os.path.isdir(file_dir):
                cn = cn + 1
                canvas_number = 'p'+str(cn)+'.json'
                image_url_id = base_url+'/'+file_path
                service['context'] = 'http://iiif.io/api/image/2/context.json' 
                service['id']  = image_url_id
                service['profile'] = 'http://iiif.io/api/image/2/level0.json'
                img = Image.open(file_path)
                width, height = img.size
                resource['type'] = 'Image'
                resource['format'] = 'image/jpeg'
                resource['width'] = width
                resource['height'] = height
                resource['id'] = image_url_id
                #resource['service'] = service
                mani_image['type']  = 'Annotation'
                mani_image['motivation']  = 'painting'
                mani_image['body']  = resource
                mani_image['id']  = base_url+'/'+file_dir+'/annotation/'+canvas_number
                mani_image['target']  = base_url+'/'+file_dir+'/canvas/'+canvas_number
                #canvas['label'] = 'p. '+str(cn)
                anno_page['type'] = "AnnotationPage"
                anno_page['id'] = base_url+'/'+file_dir+'/page/'+canvas_number+'/1'
                anno_page['items'] = []
                anno_page['items'].append(mani_image)
                canvas['items'] = []
                canvas['items'].append(anno_page)
                canvas['width'] = width
                canvas['height'] = height
                canvas['type'] = 'Canvas'
                canvas['id'] = base_url+'/'+file_dir+'/canvas/'+canvas_number
                canvases.append(canvas)
        #sequence['@id'] =  base_url+'/'+file_dir0+'/sequence/s1.json'
        #sequence['@type'] =  'sc:Sequence'
        #sequence['label'] =  'Current Page Order'
        sequence['items'] = canvases
        #each_manifest['items'] 
        #each_manifest['items'] = []
        each_manifest['items'] = canvases
        write_file_path = file_dir0+'/manifest_v3.json'
        with open(write_file_path, mode='w') as f:
            json.dump(each_manifest, f, ensure_ascii=False)
    
    
        title_en = each_manifest['label']['en']
        title_ja = each_manifest['label']['ja']
        head1 = '<h1>'+title_ja[0]+' / '+title_en[0]+'</h1>'
        metalabelvalue = ''
        for data in each_manifest['metadata']:
            if 'ja' in data['label']:
                metalabelvalue_ja = data['label']['ja'][0]
                metalabelvalue_ja += '</td><td> '+data['value']['ja'][0]
                metalabelvalue += '<tr><td>'+metalabelvalue_ja+'</td></tr>'
            elif 'en' in data['label']:
                if data['value']['en'][0] != data['value']['ja'][0]:
                    metalabelvalue_en = data['label']['en'][0]
                    metalabelvalue_en += '</td><td>'+data['value']['en'][0]
                    metalabelvalue += '<tr><td>'+metalabelvalue_en+'</td></tr>'
        
        metalabelvalue += '<tr><td>'+each_manifest['requiredStatement']['label']['ja'][0]+'</td>'
        metalabelvalue += '<td>'+each_manifest['requiredStatement']['value']['ja'][0]+'</td></tr>'
        metalabelvalue += '<tr><td>'+each_manifest['requiredStatement']['label']['en'][0]+'</td>'
        metalabelvalue += '<td>'+each_manifest['requiredStatement']['value']['en'][0]+'</td></tr>'
        metalabelvalue += '<tr><td>IIIFビューワ</td><td>'
        metalabelvalue += '<a href="https://projectmirador.org/embed/?iiif-content='+maniurlv3+'" target="_blank"><img class="mrlogo" src="https://dzkimgs.l.u-tokyo.ac.jp/omekas/files/asset/iiifviewers60f6d527d62a0.svg" alt="Mirador" width="25"></a>&nbsp;'
        metalabelvalue += '<a href="http://codh.rois.ac.jp/software/iiif-curation-viewer/demo/?manifest='+maniurlv3+'" target="_blank"><img class="icplogo" src="https://dzkimgs.l.u-tokyo.ac.jp/omekas/files/asset/iiifviewers60f6d527d6c67.svg" alt="ICP" width="25"></a>&nbsp;'
        metalabelvalue += '<a href="https://universalviewer.io/examples/uv/uv.html#?manifest='+maniurlv3+'" target="_blank"><img class="uvlogo" src="https://dzkimgs.l.u-tokyo.ac.jp/omekas/files/asset/iiifviewers60f6d527d67f0.jpg" alt="UV" width="25"></a>&nbsp;'
        metalabelvalue += '<a target="_blank" href="https://tify.rocks/?manifest='+maniurlv3+'" target="_blank"><img class="tify" src="https://dzkimgs.l.u-tokyo.ac.jp/omekas/files/asset/iiifviewers60f6d527d705d.svg" alt="TIFY" width="25"></a></td></tr>'
        metalabelvalue += '<tr><td>IIIF manifest <img class="iiiflogo" src="https://dzkimgs.l.u-tokyo.ac.jp/omekas/files/asset/iiifviewers60f6d527d5d02.svg" alt="iiif" width="25"></td><td><a href="'+maniurlv2+'" target="_blank">v2</a> <a href="'+maniurlv3+'" target="_blank">v3</a></td></tr>'

        style = '''
        h1{font-size:16px;}
        table{cellpadding:10px}
        '''

        htmldata = f'''
        <!DOCTYPE html>
        <html lang="ja"> 
        <head>
        <meta charset="utf-8"> 
        <title>{title_ja} / {title_en}</title> 
        <style>
        {style}
        </style>
        </head>
        <body>
        {head1}
        <table><tr><td>
        <table>
        {metalabelvalue}
        </table>
        </td><td><img src="{img_1st_url }" width="200" alt="サムネイル"/></td></tr></table>
        <a href="../">トップへ戻る</a>
        </body>
        </html>
        '''
        write_file_path = file_dir0+'/view.html'
        
        with open(write_file_path, mode='w') as f:
            f.write(htmldata)
        html_url = base_url+'/'+key+'/view.html'
        html_body = '<tr><td><a href="'+html_url+'" target="_blank">'+title_ja[0]+' / '+title_en[0]+'</a><br/>'
        if 'title_ja' in all_bib[key]: 
            html_body += all_bib[key]['author_ja'] +' / '
        if 'title_en' in all_bib[key]: 
            html_body += all_bib[key]['author_en']
        html_body += '</td><td><img src="'+img_1st_url+'" width="100"></td></tr>'
        all_html_url.append(html_body)


base_html_cont = ''
all_html_cont = ''.join(all_html_url)

base_html_file = f'''
        <!DOCTYPE html>
        <html lang="ja"> 
        <head>
        <meta charset="utf-8"> 
        <title>{base_title}</title> 
        <style>
        {style}
        </style>
        </head>
        <body>
        <h1>{base_title}</h1>
        <table>
        {all_html_cont}
        </table>
       
        </body>
        </html>
        '''
with open('index.html', mode='w') as f:
    f.write(base_html_file)