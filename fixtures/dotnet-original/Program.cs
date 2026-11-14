using System;

public static class Program
{
    public static string Answer(string value) => "rf:" + value.Trim().ToUpperInvariant();

    public static void Main(string[] args)
    {
        Console.WriteLine(Answer(args.Length == 0 ? "" : args[0]));
    }
}
