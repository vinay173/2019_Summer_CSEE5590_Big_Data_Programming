from pyspark.sql import SparkSession
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col
import sys
import os

os.environ["SPARK_HOME"] = "C:\\spark-2.3.1-bin-hadoop2.7"
os.environ["HADOOP_HOME"]="C:\\winutils"

# Create spark session
spark = SparkSession.builder.appName("ICP7").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Define input path
input_path = "C:\\Users\\Lenovo\\PycharmProjects\\M2_ICP7"

# Load data and select feature and label columns
data = spark.read.format("csv").option("header", True).option("inferSchema", True).option("delimiter", ",").load(input_path + "\\adult.csv")
data = data.withColumnRenamed("age", "label").select("label", col("education-num").alias("education-num"), col(" hours-per-week").alias("hours-per-week"),col(" education").alias("education"),col(" fnlwgt").alias("fnlwgt"),col(" sex").alias("sex"),col(" relationship").alias("relationship"))
data = data.select(data.label.cast("double"),"education-num", "hours-per-week","education","sex","fnlwgt","relationship")

new_data=data.toDF("label","education-num","hours-per-week","education","sex","fnlwgt","relationship")
indexer = StringIndexer(inputCol="education", outputCol="new_education")
indexed = indexer.fit(new_data).transform(new_data)

indexer1 = StringIndexer(inputCol="sex", outputCol="new_sex")
indexed1 = indexer1.fit(indexed).transform(indexed)

indexer2= StringIndexer(inputCol="relationship",outputCol="new_rel")
indexed2= indexer2.fit(indexed1).transform(indexed1)

indexed2=indexed2.drop("sex","education","relationship")
indexed2.show()


# Create vector assembler for feature columns
assembler = VectorAssembler(inputCols=indexed2.columns[1:], outputCol="features")
data = assembler.transform(indexed2)

# Split data into training and test data set
training, test = data.select("label", "features").randomSplit([0.6, 0.4])

# Create Decision tree model and fit the model with training dataset
dt = DecisionTreeClassifier()
model = dt.fit(training)

# Generate prediction from test dataset
predictions = model.transform(test)

# Evuluate the accuracy of the model
evaluator = MulticlassClassificationEvaluator()
accuracy = evaluator.evaluate(predictions)

# Show model accuracy
print("Accuracy:", accuracy)

# Report
predictionAndLabels = predictions.select("label", "prediction").rdd
metrics = MulticlassMetrics(predictionAndLabels)
print("Confusion Matrix:", metrics.confusionMatrix())
print("Precision:", metrics.precision())
print("Recall:", metrics.recall())
print("F-measure:", metrics.fMeasure())