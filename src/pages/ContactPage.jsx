import React from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

const ContactPage = () => {
    const { toast } = useToast();

    const handleSubmit = (e) => {
        e.preventDefault();
        toast({
            title: "Message Sent! (Simulation)",
            description: "Thank you for reaching out. We will get back to you shortly.",
        });
        e.target.reset();
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2,
            },
        },
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: 'spring',
                stiffness: 100,
            },
        },
    };

    return (
        <>
            <Helmet>
                <title>Contact Us - EduManage</title>
                <meta name="description" content="Get in touch with the EduManage team for support, demos, or any inquiries. We're here to help." />
            </Helmet>
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
                <Navbar />

                <motion.div
                    className="container mx-auto px-4 pt-40 pb-20"
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                >
                    <motion.div className="text-center mb-16" variants={itemVariants}>
                        <h1 className="text-5xl md:text-6xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                            Get in Touch
                        </h1>
                        <p className="mt-4 text-lg text-white/80 max-w-2xl mx-auto">
                            We're here to help with any questions you may have. Reach out to us and we'll respond as soon as we can.
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
                        <motion.div className="space-y-8" variants={itemVariants}>
                            <div className="flex items-start space-x-4">
                                <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center">
                                    <Mail className="w-6 h-6 text-blue-400" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold">Email Us</h3>
                                    <p className="text-white/70">Our team is here to help.</p>
                                    <a href="mailto:contact@edumanage.com" className="text-blue-400 hover:text-blue-300 transition-colors">contact@edumanage.com</a>
                                </div>
                            </div>
                            <div className="flex items-start space-x-4">
                                <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center">
                                    <Phone className="w-6 h-6 text-green-400" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold">Call Us</h3>
                                    <p className="text-white/70">Mon-Fri from 8am to 5pm.</p>
                                    <a href="tel:+1234567890" className="text-green-400 hover:text-green-300 transition-colors">(123) 456-7890</a>
                                </div>
                            </div>
                            <div className="flex items-start space-x-4">
                                <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center">
                                    <MapPin className="w-6 h-6 text-purple-400" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold">Visit Us</h3>
                                    <p className="text-white/70">Come say hello at our office HQ.</p>
                                    <p className="text-purple-400">123 Education Lane, Learning City, 12345</p>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div className="glass-effect p-8 rounded-xl border border-white/20" variants={itemVariants}>
                            <h2 className="text-3xl font-bold mb-6 text-white">Send us a message</h2>
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <Label htmlFor="firstName" className="text-white/80">First Name</Label>
                                        <Input id="firstName" placeholder="John" className="bg-white/5 border-white/20" required />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="lastName" className="text-white/80">Last Name</Label>
                                        <Input id="lastName" placeholder="Doe" className="bg-white/5 border-white/20" required />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="email" className="text-white/80">Email</Label>
                                    <Input id="email" type="email" placeholder="john.doe@example.com" className="bg-white/5 border-white/20" required />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="message" className="text-white/80">Message</Label>
                                    <textarea
                                        id="message"
                                        rows="4"
                                        placeholder="Your message here..."
                                        className="w-full bg-white/5 border-white/20 rounded-md p-2 text-white focus:ring-2 focus:ring-purple-500 transition-all"
                                        required
                                    />
                                </div>
                                <Button type="submit" size="lg" className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105">
                                    Send Message <Send className="ml-2 h-5 w-5" />
                                </Button>
                            </form>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </>
    );
};

export default ContactPage;