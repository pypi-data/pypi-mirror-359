def VectorAssemble(inputCol=0, outputCol=False):
    text_1 =r'''
        df_train, df_test = df.randomSplit([0.8, 0.2])

        cat_cols = [var for var, type in df.dtypes if type=='string' and var!='label_no_index' and var!=text_col]
        num_cols = [var for var, type in df.dtypes if type!='string' and var!='label_no_index' and var!=text_col]

        tokenizer = RegexTokenizer(inputCol=text_col, outputCol='words', pattern=r'[^a-zA-Z]+', toLowercase=True)
        c_vectorizer = CountVectorizer(inputCol='words', outputCol='features')
        idf = IDF(inputCol='features', outputCol='fv')
        indexer_label = StringIndexer(inputCol='label_no_index', outputCol='label')
        evaluator = MulticlassClassificationEvaluator(labelCol='label',metricName='accuracy')


        decision_tree = DecisionTreeClassifier(featuresCol='fv', labelCol='label')
        decision_tree_grid = (ParamGridBuilder()
                            .addGrid(decision_tree.impurity, ['gini', 'entropy'])
                            .addGrid(decision_tree.maxDepth, [5, 10, 15])
                            .build())


        models = {
            'Decision Tree':[decision_tree, decision_tree_grid]
                }
        best_models = {}

        for model_name, artifacts in models.items():
            print(model_name)
            model = artifacts[0]
            grid = artifacts[1]

            cv = CrossValidator(estimator=model, estimatorParamMaps=grid, evaluator=evaluator,
                numFolds=5)

            pipe = Pipeline(stages=[tokenizer, indexer_label, c_vectorizer, idf, cv])
            pipe = pipe.fit(df_train)

            df_train_eval = pipe.transform(df_train)
            df_test_eval = pipe.transform(df_test)

            print('K-Folds: K=5')
            print('Mejor accuracy en train', evaluator.evaluate(df_train_eval))
            print('Mejor accuracy en test', evaluator.evaluate(df_test_eval))

            best_models[model_name] = pipe

        '''

    text_2 = r'''
        cat_cols = [col for col, type in df.dtypes if type == 'string' and col!='label']
        num_cols = [col for col, type in df.dtypes if type != 'string' and col!='label']

        df_train, df_test = df.randomSplit([0.8, 0.2])

        string_indexer = StringIndexer(inputCols=cat_cols, outputCols=[col + '_idx' for col in cat_cols], handleInvalid='keep')
        ohe_indexer = OneHotEncoder(inputCols=[col + '_idx' for col in cat_cols], outputCols=[col + '_ohe' for col in cat_cols], handleInvalid='keep')
        assambler = VectorAssembler(inputCols=num_cols + [col + '_ohe' for col in cat_cols], outputCol='features_no_scaled')
        scaler = StandardScaler(inputCol='features_no_scaled', outputCol='features')
        evaluator = MulticlassClassificationEvaluator(metricName='accuracy')

        mlp_classifier = MultilayerPerceptronClassifier(layers=[121,100,2])
        mlp_grid = (ParamGridBuilder().addGrid(mlp_classifier.maxIter, [50, 75, 100]).addGrid(mlp_classifier.stepSize, [0.01, 0.1]).build())

        gbt = GBTClassifier()
        gbt_grid = (ParamGridBuilder().addGrid(gbt.maxDepth, [4, 8, 16]).addGrid(gbt.minInfoGain, [0, 0.01, 0.001]).build())

        tree = DecisionTreeClassifier()
        tree_grid = (ParamGridBuilder().addGrid(tree.maxDepth, [4,8,16]).addGrid(tree.impurity, ['entropy', 'gini']).build())

        best_models_to_save = {} 

        models_to_train = {
            'MLP':[mlp_classifier, mlp_grid],
            'GBT':[gbt, gbt_grid],
            'Decision_Tree': [tree, tree_grid]
        }

        for model_name, artifacts in models_to_train.items():
            print(model_name)
            model = artifacts[0]
            grid = artifacts[1]

            cv = CrossValidator(numFolds=3, estimator=model, estimatorParamMaps=grid, evaluator=evaluator)

            pipeline = Pipeline(stages = [string_indexer, ohe_indexer, assambler, scaler, cv])
            pipe = pipeline.fit(df_train)

            cv_models = pipe.stages[-1]
            best_model = cv_models.bestModel
            best_parameters = {param.name: value for param, value in best_model.extractParamMap().items()}

            print('Mejores hiperparametros (K=3)', best_parameters)
            print('Accuracy en train', evaluator.evaluate(pipe.transform(df_train)))
            print('Accuracy en test', evaluator.evaluate(pipe.transform(df_test)))

            best_models_to_save[model_name] = pipe
        '''


    text_3=r'''
        folds = df.randomSplit([1.0,1.0,1.0,1.0,1.0]) 

        str_indexer = StringIndexer(inputCols=cat_cols, outputCols=[col + '_idx' for col in cat_cols], handleInvalid='keep')
        ohe = OneHotEncoder(inputCols=[col + '_idx' for col in cat_cols], outputCols=[col + '_ohe' for col in cat_cols], handleInvalid='keep')
        assembler = VectorAssembler(inputCols=[col + '_idx' for col in cat_cols]+num_cols, outputCol='features_sin_s')
        scaler = StandardScaler(inputCol='features_sin_s', outputCol='features')
        evaluator = RegressionEvaluator()

        minInfoGains = [0.01, 0.001, 0.1]
        maxDepths = [4,8,16]
        complete_pipeline = []
        performances = []

        for minInfoGain in minInfoGains:
            for maxDepth in maxDepths:
                model = RandomForestRegressor()
                parameters = {'minInfoGain': minInfoGain, 'maxDepth': maxDepth}
                model = model.setParams(**parameters)
                evaluation_output = []

                for k_fold in range(len(folds)):
                    pipe = Pipeline(stages=[str_indexer, ohe, assembler, scaler, model])
                    dfs_to_train = folds[:k_fold] + folds[k_fold + 1:]
                    df_train = dfs_to_train[0].unionAll(dfs_to_train[1].unionAll(dfs_to_train[2]).unionAll(dfs_to_train[3]))
                    df_test = folds[k_fold]
                    pipe = pipe.fit(df_train)
                
                    df_train_eval = pipe.transform(df_train)
                    df_test_eval = pipe.transform(df_test)
                    evaluation_output.append(evaluator.evaluate(df_test_eval))
                
                complete_pipeline.append(pipe)

                mean_performance = np.mean(evaluation_output)
                performances.append(mean_performance)
                
                print(parameters)
                print('RMSE promedio 5 folds: ', round(mean_performance, 2))
                print('--'*40)

        best_pipeline = complete_pipeline[np.argsort(performances)[0]]

        '''

    text_4 = r'''
        regex = RegexTokenizer(inputCol='tweet', outputCol='tokens', toLowercase=True, pattern=r'[^a-zA-Z]')
        counter = CountVectorizer(inputCol='tokens', outputCol='fv', vocabSize=1000)
        idf = IDF(inputCol='fv', outputCol='fv_non_scaled')
        scaler = StandardScaler(inputCol='fv_non_scaled', outputCol='features')
        evaluator = ClusteringEvaluator(metricName='silhouette')

        k_values = [i for i in range(3, 4)]
        siluetes = []
        modelos = []


        for k_value in k_values:
            model = KMeans(k=k_value)
            pipe = Pipeline(stages=[regex, counter, idf,scaler, model])
            pipe = pipe.fit(df_train)
            df_test_eval = pipe.transform(df_test)
            silueta = evaluator.evaluate(df_test_eval)
            print(k_value, '| Silueta:', silueta)
            siluetes.append(silueta)
            modelos.append(pipe)

        plt.plot(siluetes)
        plt.xticks([i for i in range(len(siluetes))],[i+1 for i in range(len(siluetes))])
        plt.xlabel('Número de centroides')
        plt.ylabel('Silueta')
        plt.show()

        best_kmeans_pipeline = modelos[0]
        df_train = best_kmeans_pipeline.transform(df_train)
        kmeans_best_model = best_kmeans_pipeline.stages[-1]
        centroids = kmeans_best_model.clusterCenters()
        centroids = np.stack(centroids).tolist()
        '''


    text_5 = r'''
        just_preprocessing_pipeline = Pipeline(stages=best_kmeans_pipeline.stages[:-1])
        just_preprocessing_pipeline = just_preprocessing_pipeline.fit(df_train)
        df_test = just_preprocessing_pipeline.transform(df_test)

        temp = df_train.groupBy('prediction', 'label_no_index').count().orderBy('count', ascending=False).dropDuplicates(subset=['prediction'])
        temp.show()
        temp = temp.drop('count')

        @udf(returnType=IntegerType())
        def udf_distance(vector):
            vec_list = list(vector)
            distances = cdist([vec_list], centroids)
            closest_centroid = int(np.argmin(distances))
            return closest_centroid

        df_test = df_test.withColumn('closet_cluster', udf_distance(df_test['features']))

        temp = temp.withColumnRenamed('label_no_index', 'prediction_class')

        list_dicts = temp.toJSON().map(lambda x: json.loads(x)).collect()

        ordered_dictionary = {dictionary['prediction']: dictionary['prediction_class'] for dictionary in list_dicts}

        @udf (returnType=StringType()) 
        def get_class(int_class):
        return ordered_dictionary[int_class]

        df_test = df_test.withColumn('prediction_class', get_class(col('closet_cluster')))

        str_indexer = StringIndexer(inputCols = ['label_no_index', 'prediction_class'], outputCols=['label', 'prediction_idx'])
        str_indexer = str_indexer.fit(df_test)
        df_test = str_indexer.transform(df_test)
        evaluator = MulticlassClassificationEvaluator(metricName='accuracy', labelCol='label', predictionCol='prediction_idx')
        evaluator.evaluate(df_test)
        '''
    
    text_6 = r'''
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import udf, col, collect_list, row_number
    from pyspark.sql.types import FloatType, IntegerType
    from collections import Counter
    import math
    from pyspark.sql.window import Window


    def euclidean_distance(v1, v2):
        return float(math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))))

    distance_udf = udf(lambda a, b: euclidean_distance(a, b), FloatType())

    df_train_renamed = df_train.select(
        col("id").alias("train_id"),
        col("features").alias("train_features"),
        col("label").alias("train_label")
    )

    df_cross = df_test.crossJoin(df_train_renamed)
    df_cross = df_cross.withColumn("distance", distance_udf(col("features"), col("train_features")))

    k = 3
    window_spec = Window.partitionBy("id").orderBy("distance")

    df_knn = df_cross.withColumn("rank", row_number().over(window_spec)).filter(col("rank") <= k)

    def majority_vote(labels):
        return int(Counter(labels).most_common(1)[0][0])

    vote_udf = udf(majority_vote, IntegerType())

    df_result = (
        df_knn.groupBy("id")
        .agg(collect_list("train_label").alias("neighbors"))
        .withColumn("prediction", vote_udf(col("neighbors")))
    )
    df_result.show(truncate=False)
    '''

    text_7 = r''' 
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import udf, col, collect_list, explode, lit, array
        from pyspark.sql.types import ArrayType, StringType, MapType, IntegerType

        spark = SparkSession.builder.appName("CustomCountVectorizer").getOrCreate()


        def tokenize(text):
            return text.lower().split()

        tokenize_udf = udf(tokenize, ArrayType(StringType()))
        df_tokens = df.withColumn("tokens", tokenize_udf(col("text")))

        all_tokens = df_tokens.select(explode(col("tokens")).alias("word"))
        vocab = all_tokens.distinct().rdd.map(lambda r: r.word).zipWithIndex().collectAsMap()

        def count_vectorize(tokens):
            vocab = vocab_broadcast.value
            vec = [0] * len(vocab)
            for word in tokens:
                if word in vocab:
                    idx = vocab[word]
                    vec[idx] += 1
            return vec

        vectorize_udf = udf(count_vectorize, ArrayType(IntegerType()))
        df_vectorized = df_tokens.withColumn("features", vectorize_udf(col("tokens")))

        df_vectorized.select("id", "tokens", "features").show(truncate=False)
    '''

    text_8 = '''
        rdd = spark.sparkContext.parallelize(data)
        rdd_transformed = rdd.map(lambda x: (x[0], x[1].upper()))
        df = rdd_transformed.toDF(["id", "animal"])
        df.show()
        
        from pyspark.sql.functions import when, col
        df = spark.createDataFrame(data, ["id", "score"])
        
        df = df.withColumn(
            "categoria",
            when(col("score") >= 70, "Alto")
            .when(col("score") >= 50, "Medio")
            .otherwise("Bajo")
        )
        df.show()
    '''

    texts = [text_1, text_2, text_3, text_4, text_5, text_6, text_7, text_8]
    
    t = texts[inputCol]

    print(t)
