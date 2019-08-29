# -*- coding: utf-8 -*-
"""
Created on Thu May  9 13:28:51 2019

@author: bmoulay1
"""

import tensorflow as tf

node_const_1 = tf.constant(3.0, tf.float32, name='const_1')
node_const_2 = tf.constant(4.0, tf.float32, name='const_2')

node_add = tf.add(node_const_1, node_const_2)

a = tf.placeholder(tf.float32, name='a')
node_mul = node_add * a

b = tf.Variable(1.0, tf.float32, name='b')
node_sub = node_mul - b

with tf.Session() as session:
    writer = tf.summary.FileWriter('./first_step', session.graph)
    init = tf.global_variables_initializer()
    session.run(init)
    print(session.run(node_sub, {a:2.0}))
writer.close()    
