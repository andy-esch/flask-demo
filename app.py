import io
import json
import base64
import warnings

from flask import Flask, request, render_template
import matplotlib.pylab as plt
import seaborn as sns
import cartoframes


app = Flask(__name__)

# main entry point
@app.route('/')
def main():
    return '<html><body><h1>Flask is running :)</h1></body></html>'

# flexible end point!
@app.route('/hello/<string:name>')
def hello(name):
    return f'Hello, {name.title()}!'

# full blown analysis
@app.route("/kmeans", methods=['GET', ])
def kmeans():
    """k-means analysis
    Params:
        cols (str): Comma-separated list of columns in `table`.
        table (str): Name of table for data with columns `cols`.
        n_clusters (int): Number of clusters for the analysis. Defaults to 5.
        user (str): Username for CARTO account.
        key (str): User's CARTO API Key
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler, Imputer
    from cartoframes import Layer
    from cartoframes.styling import bold
    import time
    n_clusters = int(request.args.get('n_clusters', 5))
    cols = request.args.get('cols').split(',')
    table = request.args.get('table')
    user = request.args.get('user')
    key = request.args.get('key')
    debug = request.args.get('debug', False)
    outtable = request.args.get(
        'outtable',
        '{0}_kmeans_out_{1}'.format(table, str(time.time())[-5:])
    )

    if debug:
        debug_print(outtable=outtable)
    out_format = request.args.get('format', 'html')

    if not all((cols, table, user, key)):
        return json.dumps({'result': 'error'})

    cc = cartoframes.CartoContext(
            base_url='https://{}.carto.com/'.format(user),
            api_key=key)
    # gather the data
    dataframe = cc.query('''
        SELECT *
          FROM {table}
    '''.format(table=table))
    scaler = StandardScaler()
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(dataframe[cols].values)
    data = imp.transform(dataframe[cols].values)
    data = scaler.fit_transform(data)
    km = KMeans(n_clusters=n_clusters).fit(data)
    dataframe['labels'] = km.labels_
    dataframe['labels'] = dataframe['labels'].astype(str)
    warnings.warn(str(dataframe.dtypes))
    cc.write(dataframe, outtable, overwrite=True)
    if out_format != 'html':
        return json.dumps({
            'result': {
                'success': 'Table written to ' + outtable
            }
        })

    msg = ('Performing <b>k-means</b> on columns {cols} from {table} '
           'using {n} clusters.').format(cols=', '.join(cols),
                                         table=table,
                                         n=n_clusters)
    map_html = cc.map(
        layers=Layer(
            outtable,
            color={'column': 'labels', 'scheme': bold(n_clusters)}
        )
    ).data

    table_link = '{0}/dataset/{1}'.format(cc.creds.base_url(), outtable)
    return render_template(
        'kmeans.html',
        map_html=map_html,
        table=outtable,
        table_link=table_link,
        user=user,
        msg=msg,
        plot=plot(dataframe, cols, hue='labels')
    )


def plot(dataframe, cols, hue='labels'):
    """Pair plot for dataframe cols"""
    pal = sns.color_palette(['#7F3C8D', '#11A579', '#3969AC', '#F2B701',
                             '#E73F74', '#80BA5A', '#E68310', '#008695',
                             '#CF1C90', '#f97b72', '#4b4b8f', '#A5AA99'])
    sns.set(style="darkgrid")
    sns.pairplot(
        dataframe.fillna(dataframe.mean()),
        vars=cols,
        hue=hue,
        palette=pal,
        diag_kind='kde'
    )
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return '<img src="data:image/png;base64,{}" />'.format(plot_url)
